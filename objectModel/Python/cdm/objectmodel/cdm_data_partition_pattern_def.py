﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from collections import defaultdict
from datetime import datetime, timezone
from typing import cast, Dict, List, Optional, TYPE_CHECKING
import regex

from cdm.enums import CdmLogCode, CdmObjectType
from cdm.utilities import FileStatusCheckOptions, logger, ResolveOptions, StorageUtils, TraitToPropertyMap

from .cdm_file_status import CdmFileStatus
from .cdm_local_entity_declaration_def import CdmLocalEntityDeclarationDefinition
from .cdm_object_def import CdmObjectDefinition
from .cdm_trait_collection import CdmTraitCollection

if TYPE_CHECKING:
    from cdm.objectmodel import CdmCorpusContext
    from cdm.utilities import VisitCallback

regex_timeout = 1

class CdmDataPartitionPatternDefinition(CdmObjectDefinition, CdmFileStatus):
    def __init__(self, ctx: 'CdmCorpusContext', name: str) -> None:
        super().__init__(ctx)

        self._TAG = CdmDataPartitionPatternDefinition.__name__
        
        # The partition pattern name.
        self.name = name  # type: str

        # The starting location corpus path for searching for inferred data partitions.
        self.root_location = None  # type: Optional[str]

        # The glob pattern to use for searching partitions.
        self.glob_pattern = None  # type: Optional[str]

        # The regular expression to use for searching partitions.
        self.regular_expression = None  # type: Optional[str]

        # the names for replacement values from regular expression.
        self.parameters = None  # type: Optional[List[str]]

        # The corpus path for specialized schema to use for matched pattern partitions.
        self.specialized_schema = None  # type: Optional[str]

        self.last_file_status_check_time = None  # type: Optional[datetime]

        self.last_file_modified_time = None  # type: Optional[datetime]

        # --- internal ---

        self._ttpm = TraitToPropertyMap(self)

    @property
    def object_type(self) -> 'CdmObjectType':
        return CdmObjectType.DATA_PARTITION_PATTERN_DEF

    @property
    def last_child_file_modified_time(self) -> datetime:
        raise NotImplementedError()

    @last_child_file_modified_time.setter
    def last_child_file_modified_time(self, val: datetime):
        raise NotImplementedError()

    @property
    def is_incremental(self) -> bool:
        """
         Gets whether the data partition pattern is incremental.
        """
        return cast(bool, self._ttpm._fetch_property_value('isIncremental'))

    def copy(self, res_opt: Optional['ResolveOptions'] = None, host: Optional['CdmDataPartitionPatternDefinition'] = None) -> 'CdmDataPartitionPatternDefinition':
        if not res_opt:
            res_opt = ResolveOptions(wrt_doc=self)

        if not host:
            copy = CdmDataPartitionPatternDefinition(self.ctx, self.name)
        else:
            copy = host
            copy.name = self.name

        copy.root_location = self.root_location
        copy.glob_pattern = self.glob_pattern
        copy.regular_expression = self.regular_expression
        copy.parameters = list(self.parameters) if self.parameters else None
        copy.last_file_status_check_time = self.last_file_status_check_time
        copy.last_file_modified_time = self.last_file_modified_time
        if self.specialized_schema:
            copy.specialized_schema = self.specialized_schema
        self._copy_def(res_opt, copy)

        return copy

    async def file_status_check_async(self, file_status_check_options = None) -> None:
        await self._file_status_check_async_internal(file_status_check_options)

    async def _file_status_check_async_internal(self, file_status_check_options: Optional[FileStatusCheckOptions] = None) -> None:
        """Check the modified time for this object and any children."""
        with logger._enter_scope(self._TAG, self.ctx, self.file_status_check_async.__name__):
            namespace = None
            adapter = None

            # make sure the root is a good full corpus path.
            root_cleaned = (self.root_location[:-1] if self.root_location and self.root_location.endswith('/') else self.root_location) or ''
            root_corpus = self.ctx.corpus.storage.create_absolute_corpus_path(root_cleaned, self.in_document)

            try:
                # Remove namespace from path
                path_tuple = StorageUtils.split_namespace_path(root_corpus)
                if not path_tuple:
                    logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path, CdmLogCode.ERR_STORAGE_NULL_CORPUS_PATH)
                    return True

                namespace = path_tuple[0]
                adapter = self.ctx.corpus.storage.fetch_adapter(namespace)
                                
                if adapter is None:
                    logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path, CdmLogCode.ERR_DOC_ADAPTER_NOT_FOUND, self.in_document.name)

                # get a list of all corpus_paths under the root.
                file_info_list = await adapter.fetch_all_files_metadata_async(path_tuple[1])
            except Exception as e:
                file_info_list = None
                logger.warning(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path,
                               CdmLogCode.WARN_PARTITION_FILE_FETCH_FAILED, root_corpus, e)

            # update modified times.
            self.last_file_status_check_time = datetime.now(timezone.utc)

            if file_info_list is None:
                logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path,
                CdmLogCode.ERR_FETCHING_FILE_METADATA_NULL, namespace)
                return True

            if namespace is not None:
                # remove root of the search from the beginning of all paths so anything in the root is not found by regex.
                cleaned_file_list = {(namespace + ':' + k)[len(root_corpus):]: v for k,v in file_info_list.items()}

                if isinstance(self.owner, CdmLocalEntityDeclarationDefinition):
                    local_ent_dec_def_owner = cast('CdmLocalEntityDeclarationDefinition', self.owner)
                    # if both are present log warning and use glob pattern, otherwise use regularExpression
                    if self.glob_pattern and not self.glob_pattern.isspace() and self.regular_expression and not self.regular_expression.isspace():
                        logger.warning(self.ctx, self._TAG,CdmDataPartitionPatternDefinition.file_status_check_async.__name__,
                                       self.at_corpus_path,
                                       CdmLogCode.WARN_PARTITION_GLOB_AND_REGEX_PRESENT,
                                       self.glob_pattern, self.regular_expression)
                    regular_expression = self.glob_pattern_to_regex(
                        self.glob_pattern) if self.glob_pattern and not self.glob_pattern.isspace() else self.regular_expression

                    try:
                        reg = regex.compile(regular_expression)
                    except Exception as e:
                        logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path, CdmLogCode.ERR_VALDN_INVALID_EXPRESSION,
                                     'glob pattern' if self.glob_pattern and not self.glob_pattern.isspace(
                                     ) else 'regular expression', self.glob_pattern if self.glob_pattern and not self.glob_pattern.isspace() else self.regular_expression, e)

                    if reg:
                        # a set to check if the data partition exists
                        data_partition_path_set = set()
                        if local_ent_dec_def_owner.data_partitions is not None:
                            for data_partition in local_ent_dec_def_owner.data_partitions:
                                data_partition_location_full_path = self.ctx.corpus.storage.create_absolute_corpus_path(data_partition.location, self.in_document)
                                data_partition_path_set.add(data_partition_location_full_path)

                        incremental_partition_path_hash_set = set()
                        if local_ent_dec_def_owner.data_partitions is not None:
                            for incremental_partition in local_ent_dec_def_owner.incremental_partitions:
                                incremental_partition_location_full_path = self.ctx.corpus.storage.create_absolute_corpus_path(incremental_partition.location, self.in_document)
                                incremental_partition_path_hash_set.add(incremental_partition_location_full_path)

                        if file_status_check_options is not None and 'regex_timeout_seconds' in file_status_check_options:
                            configured_regex_timeout = file_status_check_options['regex_timeout_seconds']
                        else:
                            configured_regex_timeout = regex_timeout

                        for file_name,partition_metadata in cleaned_file_list.items():
                            try:
                                m = reg.fullmatch(file_name, timeout=configured_regex_timeout)
                            except TimeoutError as e:
                                logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path, CdmLogCode.ERR_REGEX_TIMEOUT)

                                # do not continue processing the manifest/entity/partition pattern if timeout
                                return False

                            if m:
                                # create a map of arguments out of capture groups.
                                args = defaultdict(list)  # type: Dict[str, List[str]]
                                i_param = 0
                                for i in range(1, reg.groups + 1):
                                    captures = m.captures(i)
                                    if captures and self.parameters and i_param < len(self.parameters):
                                        # to be consistent with other languages, if a capture group captures
                                        # multiple things, only use the last thing that was captured
                                        single_capture = captures[-1]

                                        current_param = self.parameters[i_param]
                                        args[current_param].append(single_capture)
                                        i_param += 1
                                    else:
                                        break

                                # put the original but cleaned up root back onto the matched doc as the location stored in the partition.
                                location_corpus_path = root_cleaned + file_name
                                full_path = root_corpus + file_name
                                # Remove namespace from path
                                path_tuple = StorageUtils.split_namespace_path(full_path)
                                if not path_tuple:
                                    logger.error(self.ctx, self._TAG, CdmDataPartitionPatternDefinition.file_status_check_async.__name__, self.at_corpus_path, CdmLogCode.ERR_STORAGE_NULL_CORPUS_PATH)
                                    return True
                                
                                exhibits_traits = self.exhibits_traits
                                if file_status_check_options is not None and 'include_data_partition_size' in file_status_check_options and partition_metadata is not None and 'file_size_bytes' in partition_metadata is not None:
                                    exhibits_traits = CdmTraitCollection(self.ctx, self)
                                    for trait in self.exhibits_traits:
                                        exhibits_traits.append(trait)
                                    exhibits_traits.append('is.partition.size', [['value', partition_metadata['file_size_bytes']]])

                                last_modified_time = await adapter.compute_last_modified_time_async(path_tuple[1])

                                if self.is_incremental and full_path not in incremental_partition_path_hash_set:
                                    local_ent_dec_def_owner._create_partition_from_pattern(
                                        location_corpus_path, exhibits_traits, args, self.specialized_schema, last_modified_time, True, self.name)
                                    incremental_partition_path_hash_set.add(full_path)

                                if not self.is_incremental and full_path not in data_partition_path_set:
                                    local_ent_dec_def_owner._create_partition_from_pattern(
                                        location_corpus_path, exhibits_traits, args, self.specialized_schema, last_modified_time)
                                    data_partition_path_set.add(full_path)
            return True


    def glob_pattern_to_regex(self, pattern: str) -> str:
        new_pattern = []

        # all patterns should start with a slash
        new_pattern.append("[/\\\\]")

        # if pattern starts with slash, skip the first character. We already added it above
        i = 1 if pattern[0] == '/' or pattern[0] == '\\' else 0
        while i < len(pattern):
            curr_char = pattern[i]

            if curr_char == '.':
                # escape '.' characters
                new_pattern.append('\\.')
            elif curr_char == '\\':
                # convert backslash into slash
                new_pattern.append('[/\\\\]')
            elif curr_char == '?':
                # question mark in glob matches any single character
                new_pattern.append('.')
            elif curr_char == '*':
                next_char = pattern[i + 1] if i + 1 < len(pattern) else None
                if next_char == '*':
                    prev_char = pattern[i - 1] if i - 1 >= 0 else None
                    post_char = pattern[i + 2] if i + 2 < len(pattern) else None

                    # globstar must be at beginning of pattern, end of pattern, or wrapped in separator characters
                    if (prev_char is None or prev_char == '/' or prev_char == '\\') and (post_char is None or post_char == '/' or post_char == '\\'):
                        new_pattern.append('.*')

                        # globstar can match zero or more subdirectories. If it matches zero, then there should not be
                        # two consecutive '/' characters so make the second one optional
                        if (prev_char == '/' or prev_char == '\\') and (post_char == '/' or post_char == '\\'):
                            new_pattern.append('/?')
                            i = i + 1
                    else:
                        # otherwise, treat the same as '*'
                        new_pattern.append('[^/\\\\]*')
                    i = i + 1
                else:
                    # *
                    new_pattern.append('[^/\\\\]*')
            else:
                new_pattern.append(curr_char)
            i = i + 1
        return ''.join(new_pattern)

    def get_name(self) -> str:
        return self.name

    def is_derived_from(self, base: str, res_opt: Optional['ResolveOptions'] = None) -> bool:
        return False

    async def report_most_recent_time_async(self, child_time: datetime) -> None:
        """Report most recent modified time (of current or children objects) to the parent object."""
        if isinstance(self.owner, CdmFileStatus) and child_time:
            await cast(CdmFileStatus, self.owner).report_most_recent_time_async(child_time)

    def validate(self) -> bool:
        if not bool(self.root_location):
            missing_fields = ['root_location']
            logger.error(self.ctx, self._TAG, 'validate', self.at_corpus_path, CdmLogCode.ERR_VALDN_INTEGRITY_CHECK_FAILURE, self.at_corpus_path, ', '.join(map(lambda s: '\'' + s + '\'', missing_fields)))
            return False
        return True

    def visit(self, path_from: str, pre_children: 'VisitCallback', post_children: 'VisitCallback') -> bool:
        path = self._fetch_declared_path(path_from)

        if pre_children and pre_children(self, path):
            return False

        if self._visit_def(path, pre_children, post_children):
            return True

        if post_children and post_children(self, path):
            return True

        return False

    def _fetch_declared_path(self, path_from: str) -> str:
        return '{}{}'.format(path_from, (self.get_name() or 'UNNAMED'))
