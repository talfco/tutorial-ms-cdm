// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

package com.microsoft.commondatamodel.objectmodel.persistence.modeljson;

import com.microsoft.commondatamodel.objectmodel.cdm.CdmCorpusContext;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmDataPartitionDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmFolderDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmTraitDefinition;
import com.microsoft.commondatamodel.objectmodel.cdm.CdmTraitReference;
import com.microsoft.commondatamodel.objectmodel.enums.CdmLogCode;
import com.microsoft.commondatamodel.objectmodel.enums.CdmObjectType;
import com.microsoft.commondatamodel.objectmodel.persistence.modeljson.types.CsvFormatSettings;
import com.microsoft.commondatamodel.objectmodel.persistence.modeljson.types.Partition;
import com.microsoft.commondatamodel.objectmodel.utilities.CopyOptions;
import com.microsoft.commondatamodel.objectmodel.utilities.ResolveOptions;
import com.microsoft.commondatamodel.objectmodel.utilities.StringUtils;
import com.microsoft.commondatamodel.objectmodel.utilities.TraitToPropertyMap;
import com.microsoft.commondatamodel.objectmodel.utilities.logger.Logger;

import java.util.List;
import java.util.concurrent.CompletableFuture;

public class DataPartitionPersistence {
  private static final String TAG = DataPartitionPersistence.class.getSimpleName();

  public static CompletableFuture<CdmDataPartitionDefinition> fromData(
      final CdmCorpusContext ctx,
      final Partition obj,
      final List<CdmTraitDefinition> extensionTraitDefList,
      final List<CdmTraitDefinition> localExtensionTraitDefList,
      final CdmFolderDefinition documentFolder) {
    final CdmDataPartitionDefinition partition = ctx.getCorpus().makeObject(CdmObjectType.DataPartitionDef, obj.getName());
    if (!StringUtils.isBlankByCdmStandard(obj.getDescription())) {
      partition.setDescription(obj.getDescription());
    }
    partition.setLocation(
        ctx.getCorpus().getStorage().createRelativeCorpusPath(
            ctx.getCorpus().getStorage().adapterPathToCorpusPath(obj.getLocation()),
            documentFolder));
    partition.setRefreshTime(obj.getRefreshTime());
    partition.setLastFileModifiedTime(obj.getLastFileModifiedTime());
    partition.setLastFileStatusCheckTime(obj.getLastFileStatusCheckTime());

    if (StringUtils.isBlankByCdmStandard(partition.getLocation())) {
      Logger.warning(ctx , TAG, "fromData", null, CdmLogCode.WarnPersistPartitionLocMissing , partition.getName());
    }

    if (obj.isHidden() != null && obj.isHidden()) {
      final CdmTraitReference isHiddenTrait = ctx.getCorpus().makeRef(CdmObjectType.TraitRef, "is.hidden", true);
      partition.getExhibitsTraits().add(isHiddenTrait);
    }

    return Utils.processAnnotationsFromData(ctx, obj, partition.getExhibitsTraits()).thenCompose(v -> {
      ExtensionHelper.processExtensionFromJson(
          ctx,
          obj,
          partition.getExhibitsTraits(),
          extensionTraitDefList,
          localExtensionTraitDefList);

      CdmTraitReference csvFormatTrait = (CdmTraitReference) partition.getExhibitsTraits().item("is.partition.format.CSV");
      if (obj.getFileFormatSettings() != null) {
        boolean partitionTraitExisted = csvFormatTrait != null;
        csvFormatTrait = Utils.createCsvTrait(obj.getFileFormatSettings(), ctx, csvFormatTrait);
        if (csvFormatTrait == null) {
          Logger.error(ctx, TAG, "fromData", null, CdmLogCode.ErrPersistCsvProcessingError);

          return CompletableFuture.completedFuture(null);
        }

        if (!partitionTraitExisted) {
          partition.getExhibitsTraits().add(csvFormatTrait);
        }
      }

      return CompletableFuture.completedFuture(partition);
    });
  }

  public static CompletableFuture<Partition> toData(
      final CdmDataPartitionDefinition instance,
      final ResolveOptions resOpt,
      final CopyOptions options) {
    final Partition result = new Partition();
    result.setName(instance.getName());
    result.setDescription(instance.getDescription());
    result.setLocation(
        instance.getCtx().getCorpus().getStorage().corpusPathToAdapterPath(
            instance.getCtx().getCorpus().getStorage().createAbsoluteCorpusPath(
                instance.getLocation(),
                instance.getInDocument())));
    result.setRefreshTime(instance.getRefreshTime());
    result.setFileFormatSettings(null);
    result.setLastFileModifiedTime(instance.getLastFileModifiedTime());
    result.setLastFileStatusCheckTime(instance.getLastFileStatusCheckTime());

    if (result.getName() == null)
    {
      Logger.warning(instance.getCtx(), TAG, "toData", instance.getAtCorpusPath(), CdmLogCode.WarnPersistPartitionNameNull);
      result.setName("");
    }

    if (StringUtils.isBlankByCdmStandard(result.getLocation())) {
      Logger.warning(instance.getCtx() , TAG, "toData", instance.getAtCorpusPath(), CdmLogCode.WarnPersistPartitionLocMissing, result.getName());
    }

    return Utils.processTraitsAndAnnotationsToData(instance.getCtx(), result, instance.getExhibitsTraits()).thenCompose(v -> {
      final TraitToPropertyMap t2pm = new TraitToPropertyMap(instance);

      if (t2pm.fetchTraitReference("is.hidden") != null) {
        result.setHidden(true);
      }

      final CdmTraitReference csvTrait = t2pm.fetchTraitReference("is.partition.format.CSV");
      if (csvTrait != null) {
        final CsvFormatSettings csvFormatSettings = Utils.createCsvFormatSettings(csvTrait);

        if (csvFormatSettings != null) {
          result.setFileFormatSettings(csvFormatSettings);
          result.getFileFormatSettings().setType("CsvFormatSettings");
        } else {
          Logger.error(instance.getCtx(), TAG, "toData", instance.getAtCorpusPath(), CdmLogCode.ErrPersistCsvProcessingError);

          return CompletableFuture.completedFuture(null);
        }
      }

      return CompletableFuture.completedFuture(result);
    });
  }
}
