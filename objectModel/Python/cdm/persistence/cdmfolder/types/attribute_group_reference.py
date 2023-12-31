﻿# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from typing import List, Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cdm.persistence.cdmfolder.types import TraitGroupReference, TraitReference

from cdm.utilities import JObject

from .attribute_group import AttributeGroup


class AttributeGroupReference(JObject):
    def __init__(self):
        super().__init__()

        self.attributeGroupReference = None  # type: Optional[Union[str, AttributeGroup]]
        self.optional = None  # type: Optional[bool]
        self.appliedTraits = None  # type: Optional[List[Union[str, 'TraitReference', 'TraitGroupReference']]]
