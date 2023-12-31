﻿// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

using System;

namespace Microsoft.CommonDataModel.ObjectModel.Utilities
{
    /// <summary>
    /// Class to contain storage-related utility methods 
    /// </summary>
    public class StorageUtils
    {
        /// <summary>
        /// The namespace separator.
        /// </summary>
        public const string namespaceSeparator = ":/";

        /// <summary>
        /// Splits the object path into the namespace and path.
        /// </summary>
        /// <param name="objectPath"></param>
        /// <returns>The tuple.</returns>
        public static Tuple<string, string> SplitNamespacePath(string objectPath)
        {
            if (objectPath == null)
            {
                return null;
            }
            string nameSpace = "";
            int separatorIndex = objectPath.IndexOf(":/");
            if (separatorIndex != -1)
            {
                nameSpace = StringUtils.Slice(objectPath, 0, separatorIndex);
                objectPath = StringUtils.Slice(objectPath, separatorIndex + 1);
            }
            return new Tuple<string, string>(nameSpace, objectPath);
        }
    }
}
