// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.
import * as fs from 'fs';
import { EOL } from 'os';
import {
    CdmArgumentDefinition,
    CdmAttributeContext,
    CdmAttributeGroupDefinition,
    CdmAttributeReference,
    CdmCollection,
    CdmConstantEntityDefinition,
    CdmAttributeItem,
    CdmEntityDefinition,
    CdmAttributeGroupReference,
    CdmObjectReference,
    CdmObjectReferenceBase,
    cdmObjectType,
    CdmTraitCollection,
    CdmTraitReference
} from '../../../internal';
import { testHelper } from '../../testHelper';

/**
 * Multiple test classes in projections test the attribute context tree generated for various scenarios.
 * This utility class helps generate the actual attribute context generated by the scenario, so that it can be compared with expected attribute context tree.
 * This also handles the validation of the expected vs. actual attribute context.
 */
export class AttributeContextUtil {
    /**
     * This string is used to concatenate all the attribute contexts and traits of an entity into one string
     * so that we can compare it to the expected output txt file.
     */
    private bldr: string = '';

    /**
     * Platform-specific line separator
     */
    private endOfLine: string = EOL;

    /**
     * Function to get the attribute context string tree from a resolved entity
     */
    public getAttributeContextStrings(resolvedEntity: CdmEntityDefinition): string {
        // clear the string builder
        this.bldr = '';

        // get the corpus path for each attribute context in the tree
        this.getContentDeclaredPath(resolvedEntity.attributeContext);

        // get the traits for all the attributes of a resolved entity
        this.getTraits(resolvedEntity.attributes);

        return this.bldr;
    }

    public getArgumentValuesAsString(args: CdmArgumentDefinition): string {
        // clear the string builder
        this.bldr = '';

        this.getArgumentValues(args);

        return this.bldr;
    }

    /**
     * Get the corpus path for each attribute context in the tree and build a string collection that we can
     * compare with the expected attribute context corpus path collection.
     */
    private getContentDeclaredPath(attribContext: CdmAttributeContext): void {
        if (attribContext && attribContext.contents && attribContext.contents.length > 0) {
            for (let i: number = 0; i < attribContext.contents.length; i++) {
                let str: string = '';
                if ((attribContext.contents.allItems[i] instanceof CdmAttributeReference)) {
                    const ar: CdmAttributeReference = attribContext.contents.allItems[i] as CdmAttributeReference;
                    str = ar.atCorpusPath;
                    this.bldr += str;
                    this.bldr += this.endOfLine;
                } else {
                    const ac: CdmAttributeContext = attribContext.contents.allItems[i] as CdmAttributeContext;
                    str = ac.atCorpusPath;
                    this.bldr += str;
                    this.bldr += this.endOfLine;
                    this.getContentDeclaredPath(ac);
                }
            }
        }
    }

    /**
     * Get the traits for all the attributes of a resolved entity
     */
    private getTraits(attributes: CdmCollection<CdmAttributeItem>): void {
        for (const attrib of attributes) {
            const attribCorpusPath: string = attrib.atCorpusPath;
            this.bldr += attribCorpusPath;
            this.bldr += this.endOfLine;

            if (attrib instanceof CdmAttributeGroupReference) {
                const attGroupDef: CdmAttributeGroupDefinition = attrib.explicitReference as CdmAttributeGroupDefinition
                this.bldr += attGroupDef.atCorpusPath;
                this.bldr += this.endOfLine;
                this.getTraitCollection(attGroupDef.exhibitsTraits);
                this.getTraits(attGroupDef.members);
            } else {
                this.getTraitCollection(attrib.appliedTraits);
            }
        }
    
    }

    private getTraitCollection(traitCollection: CdmTraitCollection): void {
        for (const trait of traitCollection) {
            const attribTraits: string = trait.namedReference;
            this.bldr += attribTraits;
            this.bldr += this.endOfLine;

            if (trait instanceof CdmTraitReference) {
                for (const args of trait.arguments) {
                    this.getArgumentValues(args);
                }
            }
        }
    } 

    private getArgumentValues(args: CdmArgumentDefinition): void {
        const paramName: string = args.resolvedParameter?.name;
        const paramDefaultValue: string = args.resolvedParameter?.defaultValue as string;

        if (paramName || paramDefaultValue) {
            this.bldr += `  [Parameter (Name / DefaultValue): ${paramName ? paramName : ''} / ${paramDefaultValue ? paramDefaultValue : ''}]`;
            this.bldr += this.endOfLine;
        }

        if (typeof args.value === 'string') {
            const argsValue: string = args.value;

            if (argsValue) {
                this.bldr += `  [Argument Value: ${argsValue}]`;
                this.bldr += this.endOfLine;
            }
        } else if ((args.value as CdmObjectReference)?.simpleNamedReference === true) {
            const argsValue: string = (args.value as CdmObjectReference).namedReference;

            if (argsValue) {
                this.bldr += `  [Argument Value: ${argsValue}]`;
                this.bldr += this.endOfLine;
            }
        } else if ((args.value as CdmObjectReference)?.explicitReference.objectType === cdmObjectType.constantEntityDef) {
            const constEnt: CdmConstantEntityDefinition = (args.value as CdmObjectReferenceBase).explicitReference as CdmConstantEntityDefinition;
            if (constEnt) {
                const refs: CdmEntityDefinition[] = [];
                for (const val of constEnt.constantValues) {
                    this.bldr += `  [Argument Value: ${val.join(',')}]`;
                    this.bldr += this.endOfLine;
                }
            }
        }
    }

    /**
     * A function to validate if the attribute context tree & traits generated for a resolved entity is the same as the expected and
     * saved attribute context tree & traits for a test case
     */
    public static async validateAttributeContext(expectedOutputPath: string, entityName: string, resolvedEntity: CdmEntityDefinition, updateExpectedOutput: boolean = false): Promise<void> {
        if (resolvedEntity.attributeContext) {
            // Actual
            const actualStringFilePath: string = `${expectedOutputPath.replace('ExpectedOutput', testHelper.getTestActualOutputFolderName())}/AttrCtx_${entityName}.txt`;
            
            // Save Actual AttrCtx_*.txt and Resolved_*.cdm.json
            const attrCtxUtil: AttributeContextUtil = new AttributeContextUtil();
            const actualText: string = attrCtxUtil.getAttributeContextStrings(resolvedEntity);
            fs.writeFileSync(actualStringFilePath, actualText);
            await resolvedEntity.inDocument.saveAsAsync(`Resolved_${entityName}.cdm.json`, false);

            // Expected
            const expectedStringFilePath: string = `${expectedOutputPath}/AttrCtx_${entityName}.txt`;
            if (updateExpectedOutput) {
                fs.writeFileSync(expectedStringFilePath, actualText);
            }
            const expectedText: string = fs.readFileSync(expectedStringFilePath).toString();

            // Test if Actual is Equal to Expected
            expect(actualText)
                .toEqual(expectedText);

        }
    }
}
