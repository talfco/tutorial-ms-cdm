// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

namespace Microsoft.CommonDataModel.ObjectModel.Storage
{
    using System;
    using System.IO;
    using System.Reflection;
    using System.Text;
    using System.Threading.Tasks;

    /// <summary>
    /// The resource adapter.
    /// </summary>
    [Obsolete("Resource Adapter is deprecated. Please install and use Microsoft.CommonDataModel.ObjectModel.Adapter.CdmStandards.")]
    public class ResourceAdapter : StorageAdapterBase
    {
        /// <summary>
        /// The resource path root (every path will have this as a start).
        /// </summary>
        private string root = "Resources";

        public ResourceAdapter()
        {
            this.root = $"{this.GetType().Assembly.GetName().Name}.{this.root}";
        }

        public override bool CanRead()
        {
            return true;
        }

        /// <inheritdoc />
        public override string CreateAdapterPath(string corpusPath)
        {
            if (string.IsNullOrEmpty(corpusPath))
            {
                return null;
            }

            return $"{root}{corpusPath}";
        }

        /// <inheritdoc />
        public override string CreateCorpusPath(string adapterPath)
        {
            if (string.IsNullOrEmpty(adapterPath) || !adapterPath.StartsWith(root))
            {
                return null;
            }

            return adapterPath.Substring(root.Length);
        }

        /// <inheritdoc />
        public override async Task<string> ReadAsync(string corpusPath)
        {
            // Convert the corpus path to the resource path.
            var resourcePath = this.CreateAdapterPath(corpusPath).Replace('/', '.').Replace('-', '_');

            // Get the resource stream.
            var assembly = Assembly.GetExecutingAssembly();
            var resourceStream = assembly.GetManifestResourceStream(resourcePath);

            if (resourceStream == null)
            {
                throw new Exception($"There is no resource found for {corpusPath}.");
            }

            using (var reader = new StreamReader(resourceStream, Encoding.UTF8))
            {
                return await reader.ReadToEndAsync();
            }
        }
    }
}