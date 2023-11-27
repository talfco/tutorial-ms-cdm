# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

import abc

class TokenProvider(abc.ABC):
    """
    Interface to be implemented by users to encapsulate their customized token provider.
    """

    @property
    @abc.abstractmethod
    def get_token(self) -> str:
        """
        Returns the token string with the authentication type included, e.g. "Bearer XXXXX"
        It is expected that the returned token has been validated for expiration upfront
        by the implementer of the interface.
        """
        raise NotImplementedError()
