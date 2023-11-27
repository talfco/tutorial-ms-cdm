// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

package com.microsoft.commondatamodel.objectmodel.utilities.network;

import java.io.Serializable;

/**
 * CDM Http Config is used for serialization purposes by network-based adapters to set up config.
 * 
 * @deprecated This class is extremely likely to be removed in the public interface, and not meant
 * to be called externally at all. Please refrain from using it.
 */
@Deprecated
class CdmHttpConfig implements Serializable {
    public long timeout;

    public long maximumTimeout;

    public int numberOfRetries;
}
