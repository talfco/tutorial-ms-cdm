﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

import datetime
import json
import warnings
from typing import Dict, List, Optional

from cdm.storage.network import NetworkAdapter
from cdm.utilities.network.cdm_http_client import CdmHttpClient

from .base import StorageAdapterBase


class GithubAdapter(NetworkAdapter, StorageAdapterBase):
    """Github storage adapter"""

    _raw_root = 'https://raw.githubusercontent.com/Microsoft/CDM/master/schemaDocuments'  # type: str

    def __init__(self) -> None:
        super().__init__()
        super(NetworkAdapter, self).__init__()
        super(StorageAdapterBase, self).__init__()

        warnings.warn('GithubAdapter is deprecated. Please use the CdmStandardsAdapter instead.', DeprecationWarning)

        # --- internal ---
        self._type = 'github'
        self._http_client = CdmHttpClient(self._raw_root)  # type: CdmHttpClient

    def can_read(self) -> bool:
        return True

    def create_adapter_path(self, corpus_path: str) -> str:
        return self._raw_root + corpus_path

    def create_corpus_path(self, adapter_path: str) -> Optional[str]:
        if adapter_path and adapter_path.startswith(self._raw_root):
            return adapter_path[len(self._raw_root):]

        # Signal that we did not recognize path as one for self adapter.
        return None

    def fetch_config(self) -> str:
        result_config = {'type': self._type}

        # construct network configs.
        config_object = {}

        config_object.update(self.fetch_network_config())

        if self.location_hint:
            config_object['locationHint'] = self.location_hint

        result_config['config'] = config_object

        return json.dumps(result_config)

    async def read_async(self, corpus_path: str) -> str:
        request = self._set_up_cdm_request(corpus_path, {'User-Agent': 'CDM'}, 'GET')
        return await super()._read(request)

    def update_config(self, config) -> None:
        if not config:
            # It is fine just to skip it for GitHub adapter.
            return

        self.update_network_config(config)

        config_json = json.loads(config)

        if config_json.get('locationHint'):
            self.location_hint = config_json["locationHint"]
