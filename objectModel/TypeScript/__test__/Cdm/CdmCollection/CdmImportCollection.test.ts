// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

import {
    CdmDocumentDefinition,
    CdmImport
} from '../../../internal';
import {generateManifest} from './CdmCollectionHelperFunctions';

describe('Cdm/CdmCollection/CdmImportCollection', () => {
    it('TestImportCollectionAdd', () => {
        const document: CdmDocumentDefinition = generateManifest();
        document.isDirty = false;
        expect(document.isDirty)
            .toEqual(false);
        const imp: CdmImport = new CdmImport(document.ctx, 'corpusPath', 'moniker');
        const addedImp: CdmImport = document.imports.push(imp);

        expect(document.isDirty)
            .toEqual(true);
        expect(document.imports.length)
            .toEqual(1);
        expect(addedImp)
            .toEqual(imp);
        expect(document.imports.allItems[0])
            .toEqual(imp);
        expect(imp.corpusPath)
            .toEqual('corpusPath');
        expect(imp.moniker)
            .toEqual('moniker');
        expect(imp.ctx)
            .toEqual(document.ctx);
    });

    it('TestCdmImportCollectionAddCorpusPath', () => {
        const document: CdmDocumentDefinition = generateManifest();
        document.isDirty = false;
        const imp: CdmImport = document.imports.push('corpusPath');

        expect(document.isDirty)
            .toEqual(true);
        expect(document.imports.length)
            .toEqual(1);
        expect(document.imports.allItems[0])
            .toEqual(imp);
        expect(imp.corpusPath)
            .toEqual('corpusPath');
        expect(imp.moniker)
            .toBeUndefined();
        expect(imp.ctx)
            .toEqual(document.ctx);
    });

    it ('TestCdmImportCollectionAddCorpusPathAndMoniker', () => {
        const document: CdmDocumentDefinition = generateManifest();
        document.isDirty = false;
        const imp: CdmImport = document.imports.push('corpusPath', 'moniker');

        expect(document.isDirty)
            .toEqual(true);
        expect(document.imports.length)
            .toEqual(1);
        expect(document.imports.allItems[0])
            .toEqual(imp);
        expect(imp.corpusPath)
            .toEqual('corpusPath');
        expect(imp.moniker)
            .toEqual('moniker');
        expect(imp.ctx)
            .toEqual(document.ctx);
    });

    it ('TestCdmImportCollectionAddRange', () => {
        const document: CdmDocumentDefinition = generateManifest();
        document.isDirty = false;
        const importList: CdmImport[] = [
            new CdmImport(document.ctx, 'corpusPath1', 'moniker1'),
            new CdmImport(document.ctx, 'corpusPath2', 'moniker2'),
            new CdmImport(document.ctx, 'corpusPath3', undefined)
        ];
        document.imports.concat(importList);

        expect(document.isDirty)
            .toBeTruthy();
        expect(document.imports.length)
            .toEqual(3);
        expect(document.imports.allItems[0])
            .toEqual(importList[0]);
        expect(document.imports.allItems[1])
            .toEqual(importList[1]);
        expect(document.imports.allItems[0].corpusPath)
            .toEqual('corpusPath1');
        expect(document.imports.item('corpusPath1', 'moniker1').moniker)
            .toEqual('moniker1');
        expect(document.imports.item('corpusPath1', 'moniker1').ctx)
            .toEqual(document.ctx);
        expect(document.imports.allItems[1].corpusPath)
            .toEqual('corpusPath2');
        expect(document.imports.item('corpusPath2'))
            .toBeUndefined();
        expect(document.imports.item('corpusPath2', undefined, false))
            .not.toBeUndefined();
        expect(document.imports.item('corpusPath2', undefined, true))
            .toBeUndefined();
        expect(document.imports.item('corpusPath2', 'moniker2', true))
            .not.toBeUndefined();
        expect(document.imports.item('corpusPath2', 'moniker3', false))
            .not.toBeUndefined();
        expect(document.imports.item('corpusPath2', 'moniker2').moniker)
            .toEqual('moniker2');
        expect(document.imports.item('corpusPath2', 'moniker2').ctx)
            .toEqual(document.ctx);
        expect(document.imports.item('corpusPath3'))
            .toEqual(importList[2]);
    });
});
