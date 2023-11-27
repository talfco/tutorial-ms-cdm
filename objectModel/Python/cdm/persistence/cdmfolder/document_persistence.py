﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from typing import List

from cdm.enums import CdmObjectType
from cdm.persistence import PersistenceLayer
from cdm.objectmodel import CdmCorpusContext, CdmDocumentDefinition, CdmEntityDefinition, CdmObject
from cdm.utilities import CopyOptions, ResolveOptions, copy_data_utils, logger
from cdm.utilities.string_utils import StringUtils

from cdm.enums import CdmLogCode
from .attribute_group_persistence import AttributeGroupPersistence
from .constant_entity_persistence import ConstantEntityPersistence
from .data_type_persistence import DataTypePersistence
from .entity_persistence import EntityPersistence
from .import_persistence import ImportPersistence
from .purpose_persistence import PurposePersistence
from .trait_persistence import TraitPersistence
from .trait_group_persistence import TraitGroupPersistence
from .types import DocumentContent

_TAG = 'DocumentPersistence'

class DocumentPersistence:
    is_persistence_async = False

    formats = [PersistenceLayer.CDM_EXTENSION]

    # The maximum json semantic version supported by this ObjectModel version
    json_semantic_version_max = CdmObject.json_schema_semantic_version_maximum_save_load
    # The minimum json semantic version supported by this ObjectModel version
    json_semantic_version_min = CdmObject.json_schema_semantic_version_minimum_save

    @staticmethod
    def from_data(ctx: 'CdmCorpusContext', doc_name: str, json_data: str, folder: 'CdmFolderDefinition') -> 'CdmDocumentDefinition':
        obj = DocumentContent().decode(json_data)
        return DocumentPersistence.from_object(ctx, doc_name, folder._namespace, folder._folder_path, obj)

    @staticmethod
    def from_object(ctx: CdmCorpusContext, name: str, namespace: str, path: str, data: 'DocumentContent') -> 'CdmDocumentDefinition':
        document = ctx.corpus.make_object(CdmObjectType.DOCUMENT_DEF, name)
        document._folder_path = path
        document._namespace = namespace

        if data:
            if not StringUtils.is_blank_by_cdm_standard(data.schema):
                document.schema = data.schema

            # support old model syntax
            if not StringUtils.is_blank_by_cdm_standard(data.schemaVersion):
                document.json_schema_semantic_version = data.schemaVersion

            if not StringUtils.is_blank_by_cdm_standard(data.documentVersion):
                document.document_version = data.documentVersion

            if data.get('imports'):
                for import_obj in data.imports:
                    document.imports.append(ImportPersistence.from_data(ctx, import_obj))

            if data.get('definitions') and isinstance(data.definitions, List):
                for definition in data.definitions:
                    if definition.get('dataTypeName'):
                        document.definitions.append(DataTypePersistence.from_data(ctx, definition))
                    elif definition.get('purposeName'):
                        document.definitions.append(PurposePersistence.from_data(ctx, definition))
                    elif definition.get('attributeGroupName'):
                        document.definitions.append(AttributeGroupPersistence.from_data(ctx, definition))
                    elif definition.get('traitName'):
                        document.definitions.append(TraitPersistence.from_data(ctx, definition))
                    elif definition.get('traitGroupName'):
                        document.definitions.append(TraitGroupPersistence.from_data(ctx, definition))
                    elif definition.get('entityShape'):
                        document.definitions.append(ConstantEntityPersistence.from_data(ctx, definition))
                    elif definition.get('entityName'):
                        document.definitions.append(EntityPersistence.from_data(ctx, definition))

            is_resolved_doc = False
            if len(document.definitions) == 1 and isinstance(document.definitions[0], CdmEntityDefinition):
                entity = document.definitions[0]  # type: CdmEntityDefinition
                resolved_trait = entity.exhibits_traits.item('has.entitySchemaAbstractionLevel')
                # Tries to figure out if the document is in resolved form by looking for the schema abstraction trait
                # or the presence of the attribute context.
                is_resolved_doc = resolved_trait and resolved_trait.arguments[0].value == 'resolved'
                is_resolved_doc = is_resolved_doc or entity.attribute_context

            if data.jsonSchemaSemanticVersion:
                document.json_schema_semantic_version = data.jsonSchemaSemanticVersion
                if DocumentPersistence._compare_json_semantic_version(ctx, document.json_schema_semantic_version) > 0:
                    if is_resolved_doc:
                        logger.warning(ctx, _TAG, DocumentPersistence.from_data.__name__, None,
                                       CdmLogCode.WARN_PERSIST_UNSUPPORTED_JSON_SEM_VER, DocumentPersistence.json_semantic_version_max, document.json_schema_semantic_version)
                    else:
                        logger.error(ctx, _TAG, DocumentPersistence.from_data.__name__, None,
                                     CdmLogCode.ERR_PERSIST_UNSUPPORTED_JSON_SEM_VER, DocumentPersistence.json_semantic_version_max, document.json_schema_semantic_version)
            else:
                logger.warning(ctx, _TAG, DocumentPersistence.from_data.__name__, document.at_corpus_path, CdmLogCode.WARN_PERSIST_JSON_SEM_VER_MANDATORY)

        return document

    @staticmethod
    def to_data(instance: CdmDocumentDefinition, res_opt: ResolveOptions, options: CopyOptions) -> DocumentContent:
        result = DocumentContent()
        result.schema = instance.schema
        result.jsonSchemaSemanticVersion = instance.json_schema_semantic_version
        result.imports = copy_data_utils._array_copy_data(res_opt, instance.imports, options)
        result.definitions = copy_data_utils._array_copy_data(res_opt, instance.definitions, options)
        result.documentVersion = instance.document_version
        return result

    @staticmethod
    def _compare_json_semantic_version(ctx: 'CdmCorpusContext', document_semantic_version: str) -> int:
        """Compares the document version with the json semantic version supported.
        1 => if document_semantic_version > json_semantic_version_max
        0 => if document_semantic_version between json_semantic_version_min and json_semantic_version_max or if document_semantic_version is invalid
        -1 => if document_semantic_version < json_semantic_version_min"""

        error_message = 'jsonSemanticVersion must be set using the format <major>.<minor>.<patch>.'

        doc_ver = CdmObject.semantic_version_string_to_number(document_semantic_version)
        if doc_ver == -1:
            logger.warning(ctx, _TAG, DocumentPersistence._compare_json_semantic_version.__name__, None,
                           CdmLogCode.WARN_PERSIST_JSON_SEM_VER_INVALID_FORMAT)
            return 0

        min_ver = CdmObject.semantic_version_string_to_number(DocumentPersistence.json_semantic_version_min)
        max_ver = CdmObject.semantic_version_string_to_number(DocumentPersistence.json_semantic_version_max)

        if doc_ver < min_ver:
            return -1
        elif doc_ver > max_ver:
            return 1
        return 0