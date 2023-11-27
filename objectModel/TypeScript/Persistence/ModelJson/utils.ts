// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

import { CdmFolder, ModelJson } from '..';
import {
    CdmArgumentDefinition,
    CdmCorpusContext,
    cdmLogCode,
    cdmObjectType,
    CdmTraitCollection,
    CdmTraitGroupReference,
    CdmTraitReference,
    CdmTraitReferenceBase,
    isCdmTraitReference,
    Logger
} from '../../internal';
import { CdmJsonType, TraitGroupReference, TraitReference } from '../CdmFolder/types';
import { processExtensionTraitToObject, traitRefIsExtension } from './ExtensionHelper';
import { Annotation, CsvFormatSettings, MetadataObject } from './types';
import { NameValuePair } from '../../Utilities/NameValuePair';
import { ArgumentPersistence } from './ArgumentPersistence';

const annotationToTraitMap: Map<string, string> = new Map([['version', 'is.CDM.entityVersion']]);

const traitToAnnotationMap: Map<string, string> = new Map([['is.CDM.entityVersion', 'version']]);

export const ignoredTraits: Set<string> = new Set<string>().add('is.modelConversion.otherAnnotations')
    .add('is.propertyContent.multiTrait')
    .add('is.modelConversion.referenceModelMap')
    .add('is.modelConversion.modelVersion')
    .add('means.measurement.version')
    .add('is.CDM.entityVersion')
    .add('is.partition.culture')
    .add('is.managedBy')
    .add('is.hidden');

// Traits to ignore if they come from properties.
// These traits become properties on the model.json. To avoid persisting both a trait
// and a property on the model.json, we filter these traits out.
export const modelJsonPropertyTraits: Set<string> = new Set<string>().add('is.localized.describedAs');

// Arguments natively supported by the fileFormatSettings property.
export const partitionSettingsSupportedArguments: Set<string> = new Set<string>()
    .add('columnHeaders')
    .add('csvStyle')
    .add('delimiter')
    .add('quoteStyle')
    .add('encoding');

export function shouldAnnotationGoIntoASingleTrait(name: string): boolean {
    return annotationToTraitMap.has(name);
}

export function convertAnnotationToTrait(name: string): string {
    return annotationToTraitMap.get(name);
}

export function convertTraitToAnnotation(name: string): string {
    return traitToAnnotationMap.get(name);
}

export function shouldPersistTrait(traitBase: CdmTraitReferenceBase): boolean {
    if (!(traitBase instanceof CdmTraitReference)) {
        return true;
    }

    const trait = traitBase as CdmTraitReference;
    switch (trait.namedReference) {
        case "is.partition.format.CSV":
            var argumentNames = trait.arguments.allItems.filter(arg => !!arg.name).map(arg => arg.name);

            // Checks if the trait contains arguments that are not supported natively by the model.json CsvFormatSettings property.
            return argumentNames.filter(argName => !partitionSettingsSupportedArguments.has(argName)).length > 0;
        default:
            return true;
    }
}

export function createCsvTrait(object: CsvFormatSettings, ctx: CdmCorpusContext, host: CdmTraitReference): CdmTraitReference {
    const csvFormatTrait: CdmTraitReference = host ?? ctx.corpus.MakeObject(cdmObjectType.traitRef, 'is.partition.format.CSV', false);
    var argumentNames = new Set<string>(csvFormatTrait.arguments.allItems.filter(arg => !arg.name).map(arg => arg.name));

    if (object.columnHeaders !== undefined && !argumentNames.has('columnHeaders')) {
        const columnHeadersArg: CdmArgumentDefinition = ctx.corpus.MakeObject(cdmObjectType.argumentDef, 'columnHeaders');
        columnHeadersArg.value = object.columnHeaders === 'true' || object.columnHeaders === true ? 'true' : 'false';
        csvFormatTrait.arguments.push(columnHeadersArg);
    }

    if (object.csvStyle !== undefined && !argumentNames.has('csvStyle')) {
        const csvStyleArg: CdmArgumentDefinition = ctx.corpus.MakeObject(cdmObjectType.argumentDef, 'csvStyle');
        csvStyleArg.value = object.csvStyle;
        csvFormatTrait.arguments.push(csvStyleArg);
    }

    if (object.delimiter !== undefined && !argumentNames.has('delimiter')) {
        const delimiterArg: CdmArgumentDefinition = ctx.corpus.MakeObject(cdmObjectType.argumentDef, 'delimiter');
        delimiterArg.value = object.delimiter;
        csvFormatTrait.arguments.push(delimiterArg);
    }

    if (object.quoteStyle !== undefined && !argumentNames.has('quoteStyle')) {
        const quoteStyleArg: CdmArgumentDefinition = ctx.corpus.MakeObject(cdmObjectType.argumentDef, 'quoteStyle');
        quoteStyleArg.value = object.quoteStyle;
        csvFormatTrait.arguments.push(quoteStyleArg);
    }

    if (object.encoding !== undefined && !argumentNames.has('encoding')) {
        const encodingArg: CdmArgumentDefinition = ctx.corpus.MakeObject(cdmObjectType.argumentDef, 'encoding');
        encodingArg.value = object.encoding;
        csvFormatTrait.arguments.push(encodingArg);
    }

    return csvFormatTrait;
}

export function createCsvFormatSettings(csvFormatTrait: CdmTraitReference): CsvFormatSettings {
    const result: CsvFormatSettings = <CsvFormatSettings>{};

    for (const argument of csvFormatTrait.arguments.allItems) {
        if (argument.name === 'columnHeaders') {
            result.columnHeaders = argument.value === 'true';
        }

        if (argument.name === 'csvStyle') {
            result.csvStyle = argument.value as string;
        }

        if (argument.name === 'delimiter') {
            result.delimiter = argument.value as string;
        }

        if (argument.name === 'quoteStyle') {
            result.quoteStyle = argument.value as string;
        }

        if (argument.name === 'encoding') {
            result.encoding = argument.value as string;
        }
    }

    return result;
}

export async function processAnnotationsFromData(ctx: CdmCorpusContext, object: MetadataObject, traits: CdmTraitCollection)
    : Promise<void> {
    const multiTraitAnnotations: NameValuePair[] = [];

    if (object.annotations !== undefined) {
        for (const annotation of object.annotations) {
            if (!shouldAnnotationGoIntoASingleTrait(annotation.name)) {
                const cdmElement: NameValuePair = new NameValuePair();
                cdmElement.name = annotation.name;
                cdmElement.value = annotation.value;
                multiTraitAnnotations.push(cdmElement);
            } else {
                const innerTrait: CdmTraitReference =
                    ctx.corpus.MakeObject(cdmObjectType.traitRef, convertAnnotationToTrait(annotation.name));
                innerTrait.arguments.push(await ModelJson.ArgumentPersistence.fromData(ctx, annotation));
                traits.push(innerTrait);
            }
        }

        if (multiTraitAnnotations.length > 0) {
            const trait: CdmTraitReference =
                ctx.corpus.MakeObject(cdmObjectType.traitRef, 'is.modelConversion.otherAnnotations', false);
            trait.isFromProperty = false;

            const annotationsArguemnt: CdmArgumentDefinition = new CdmArgumentDefinition(ctx, 'annotations');
            annotationsArguemnt.value = multiTraitAnnotations;
            trait.arguments.push(annotationsArguemnt);
            traits.push(trait);
        }
    }

    if (object['cdm:traits'] !== undefined) {
        object['cdm:traits'].forEach((trait: string | TraitReference | TraitGroupReference) => {
            if (typeof trait !== 'string' && 'traitGroupReference' in trait) {
                traits.push(CdmFolder.TraitGroupReferencePersistence.fromData(ctx, trait as TraitGroupReference));
            } else {
                traits.push(CdmFolder.TraitReferencePersistence.fromData(ctx, trait));
            }
        });
    }
}

export async function processTraitsAndAnnotationsToData(
    ctx: CdmCorpusContext,
    entityObject: MetadataObject,
    traits: CdmTraitCollection): Promise<void> {
    if (traits === undefined) {
        return;
    }

    const annotations: Annotation[] = [];

    const extensions: CdmJsonType[] = [];

    for (const trait of traits) {
        if (traitRefIsExtension(trait)) {
            // Safe to cast since extensions can only be trait refs, not trait group refs
            processExtensionTraitToObject(trait as CdmTraitReference, entityObject);
        } else if (trait.namedReference === 'is.modelConversion.otherAnnotations') {
            // Safe to cast since extensions can only be trait refs, not trait group refs
            for (const annotation of ((trait as CdmTraitReference).arguments.allItems[0].value as any)) {
                if (annotation instanceof NameValuePair) {
                    const element: Annotation = new Annotation();
                    element.name = annotation.name;
                    element.value = annotation.value;
                    annotations.push(element);
                } 
                else if (typeof annotation === 'object') {
                    annotations.push(annotation);
                } else {
                    Logger.warning(ctx, this.TAG, this.processTraitsAndAnnotationsToData.name, trait.atCorpusPath, cdmLogCode.WarnAnnotationTypeNotSupported);
                }
            }
        } else if (isCdmTraitReference(trait) && traitToAnnotationMap.has(trait.namedReference)) {
            const element: Annotation = await ArgumentPersistence.toData(trait.arguments.allItems[0], undefined, undefined);
            element.name = convertTraitToAnnotation(trait.namedReference);
            annotations.push(element);
        } else if (!ignoredTraits.has(trait.namedReference)
                    && !trait.namedReference.startsWith('is.dataFormat')
                    && !(modelJsonPropertyTraits.has(trait.namedReference) && trait instanceof CdmTraitReference && (trait as CdmTraitReference).isFromProperty)
                    && shouldPersistTrait(trait)) {
            if (trait instanceof CdmTraitGroupReference) {
                extensions.push(CdmFolder.TraitGroupReferencePersistence.toData(trait, undefined, undefined));
            } else {
                extensions.push(CdmFolder.TraitReferencePersistence.toData(trait, undefined, undefined));
            }
        }

        if (annotations.length > 0) {
            entityObject.annotations = annotations;
        }

        if (extensions.length > 0) {
            entityObject['cdm:traits'] = extensions;
        }
    }
}
