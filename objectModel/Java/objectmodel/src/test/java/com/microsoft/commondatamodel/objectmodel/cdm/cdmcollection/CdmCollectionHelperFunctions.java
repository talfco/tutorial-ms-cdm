// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

package com.microsoft.commondatamodel.objectmodel.cdm.cdmcollection;

import com.microsoft.commondatamodel.objectmodel.TestHelper;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmCorpusDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmDocumentDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmEntityDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmFolderDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmManifestDefinition;
import com.microsoft.commondatamodel.objectmodel.enums.CdmObjectType;
import com.microsoft.commondatamodel.objectmodel.persistence.CdmConstants;

public class CdmCollectionHelperFunctions {
  /**
   * Creates a Manifest used for the tests.
   *
   * @return Created Manifest.
   */
  static CdmManifestDefinition generateManifest() throws InterruptedException {
    final CdmCorpusDefinition cdmCorpus = TestHelper.getLocalCorpus(null, "generateManifest", null, null, true);
    final CdmManifestDefinition manifest = new CdmManifestDefinition(cdmCorpus.getCtx(), "manifest");
    manifest.setFolderPath("/");
    manifest.setNamespace("local");

    return manifest;
  }

  public static CdmDocumentDefinition createDocumentForEntity(
          final CdmCorpusDefinition cdmCorpus,
          final CdmEntityDefinition entity) {
    return createDocumentForEntity(cdmCorpus, entity, "local");
  }

  /**
   * For an entity, it creates a document that will contain the entity.
   *
   * @param cdmCorpus The corpus everything belongs to.
   * @param entity    The entity we want a document for.
   * @param nameSpace The nameSpace of the adapter.
   * @return A document containing desired entity.
   */
  static CdmDocumentDefinition createDocumentForEntity(
      final CdmCorpusDefinition cdmCorpus,
      final CdmEntityDefinition entity,
      final String nameSpace) {
    final CdmFolderDefinition cdmFolderDef = cdmCorpus.getStorage().fetchRootFolder(nameSpace);
    final CdmDocumentDefinition entityDoc = cdmCorpus.makeObject(
        CdmObjectType.DocumentDef,
        entity.getEntityName() + CdmConstants.CDM_EXTENSION,
        false);

    cdmFolderDef.getDocuments().add(entityDoc);
    entityDoc.getDefinitions().add(entity);
    return entityDoc;
  }
}
