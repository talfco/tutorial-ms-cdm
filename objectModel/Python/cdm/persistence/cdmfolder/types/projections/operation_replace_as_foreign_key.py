# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from cdm.persistence.cdmfolder.types.type_attribute import TypeAttribute
from cdm.persistence.cdmfolder.types.projections.operation_base import OperationBase


class OperationReplaceAsForeignKey(OperationBase):
    """OperationReplaceAsForeignKey class"""

    def __init__(self):
        super().__init__()

        self.reference = None  # type: str
        self.replaceWith = None  # type: TypeAttribute
