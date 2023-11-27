// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

namespace Microsoft.CommonDataModel.ObjectModel.Tests.Cdm.CdmCollection
{
    using Microsoft.CommonDataModel.ObjectModel.Cdm;
    using Microsoft.CommonDataModel.ObjectModel.Storage;
    using Microsoft.CommonDataModel.ObjectModel.Utilities;
    using Microsoft.CommonDataModel.Tools.Processor;

    public static class CdmCollectionHelperFunctions
    {

        /// <summary>
        /// Creates a manifest used for the tests.
        /// </summary>
        /// <returns>Created corpus.</returns>
        public static CdmManifestDefinition GenerateManifest()
        {
            var cdmCorpus = TestHelper.GetLocalCorpus(null, nameof(GenerateManifest), noInputAndOutputFolder: true);

            var manifest = new CdmManifestDefinition(cdmCorpus.Ctx, "manifest");
            manifest.FolderPath = "/";
            manifest.Namespace = "local";

            return manifest;
        }

        /// <summary>
        /// For an entity, it creates a document that will contain the entity.
        /// </summary>
        /// <param name="cdmCorpus">The corpus everything belongs to.</param>
        /// <param name="entity">The entity we want a document for.</param>
        /// <returns>A document containing desired entity.</returns>
        public static CdmDocumentDefinition CreateDocumentForEntity(CdmCorpusDefinition cdmCorpus, CdmEntityDefinition entity, string nameSpace = "local")
        {
            var cdmFolderDef = cdmCorpus.Storage.FetchRootFolder(nameSpace);
            var entityDoc = cdmCorpus.MakeObject<CdmDocumentDefinition>(Enums.CdmObjectType.DocumentDef, $"{entity.EntityName}.cdm.json", false);

            cdmFolderDef.Documents.Add(entityDoc);
            entityDoc.Definitions.Add(entity);
            return entityDoc;
        }
    }
}
