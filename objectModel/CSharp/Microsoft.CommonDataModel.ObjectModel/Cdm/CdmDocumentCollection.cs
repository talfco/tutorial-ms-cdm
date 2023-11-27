// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

namespace Microsoft.CommonDataModel.ObjectModel.Cdm
{
    using Microsoft.CommonDataModel.ObjectModel.Enums;
    using System.Collections.Generic;
    using Microsoft.CommonDataModel.ObjectModel.Utilities.Logging;

    /// <summary>
    /// <see cref="CdmCollection"/> customized for <see cref="CdmDocumentDefinition"/>.
    /// </summary>
    public class CdmDocumentCollection : CdmCollection<CdmDocumentDefinition>
    {
        private static readonly string Tag = nameof(CdmDocumentCollection);

        /// < inheritdoc/>
        protected new CdmFolderDefinition Owner
        {
            get
            {
                return base.Owner as CdmFolderDefinition;
            }
        }

        /// <summary>
        /// Constructs a CdmDocumentCollection by using the parent constructor and DocumentDef as the default type.
        /// </summary>
        /// <param name="ctx">The context.</param>
        /// <param name="owner">The folder that contains this collection.</param>
        public CdmDocumentCollection(CdmCorpusContext ctx, CdmFolderDefinition owner)
            : base(ctx, owner, CdmObjectType.DocumentDef)
        {
        }

        /// <inheritdoc />
        public new bool Insert(int index, CdmDocumentDefinition document)
        {
            if (!this.CheckAndAddItemModifications(document))
                return false;

            // why is this collection unlike all other collections?
            // because documents are in folders. folders are not in documents.
            document.Owner = this.Owner;
            lock (AllItems)
            {
                this.AllItems.Insert(index, document);
            }
            return true;
        }

        /// < inheritdoc/>
        public new CdmDocumentDefinition Add(CdmDocumentDefinition document)
        {
            if (!this.CheckAndAddItemModifications(document))
                return null;

            // why is this collection unlike all other collections?
            // because documents are in folders. folders are not in documents.
            document.Owner = this.Owner;
            lock (AllItems)
            {
                AllItems.Add(document);
            }
            return document;
        }

        /// <summary>
        /// Adds a document to the collection after it sets the name with the given parameter.
        /// </summary>
        /// <param name="document">The document to be added to the collection.</param>
        /// <param name="documentName">The name of the document will be set to this value.</param>
        /// <returns>The document that was added to the collection.</returns>
        public CdmDocumentDefinition Add(CdmDocumentDefinition document, string documentName)
        {
            document.Name = documentName;
            return this.Add(document);
        }

        /// < inheritdoc />
        public new CdmDocumentDefinition Add(string name, bool simpleRef = false)
        {
            var document = this.Ctx.Corpus.MakeObject<CdmDocumentDefinition>(this.DefaultType, name, simpleRef);
            return this.Add(document);
        }

        /// <inheritdoc />
        public new void AddRange(IEnumerable<CdmDocumentDefinition> documents)
        {
            foreach (var document in documents)
            {
                this.Add(document);
            }
        }

        /// < inheritdoc/>
        public new bool Remove(CdmDocumentDefinition document)
        {
            return this.Remove(document.Name);
        }

        /// <summary>
        /// Removes the document with the specified name from the collection.
        /// </summary>
        /// <param name="name">The name of the document to be removed from the collection.</param>
        /// <returns>Whether the operation completed successfully.</returns>
        public bool Remove(string name)
        {
            if (this.Owner.DocumentLookup.ContainsKey(name))
            {
                this.RemoveItemModifications(name);
                int index;
                lock (AllItems)
                {
                    index = this.AllItems.FindIndex((d) => string.Equals(d.Name, name));
                }
                // setting this currentlyResolving flag will keep the base collection code from setting the inDocument to null
                // this makes sense because a document is "in" itself. always.
                bool bSave = this.Ctx.Corpus.isCurrentlyResolving;
                this.Ctx.Corpus.isCurrentlyResolving = true;
                base.RemoveAt(index);
                this.Ctx.Corpus.isCurrentlyResolving = bSave;
                return true;
            }
            return false;
        }

        /// <inheritdoc />
        public new void RemoveAt(int index)
        {
            lock (AllItems)
            {
                if (index >= 0 && index < this.AllItems.Count)
                {
                    this.Remove(this.AllItems[index].Name);
                }
            }
        }

        /// <inheritdoc />
        public new void Clear()
        {
            lock (AllItems)
            {
                this.AllItems.ForEach((doc) => this.RemoveItemModifications(doc.Name));
            }
            base.Clear();
        }

        /// <summary>
        /// Check if document already added, if not then performs changes to an item that is added to the collection.
        /// Does not actually add the item to the collection.
        /// </summary>
        /// <param name="document">The item that needs to be changed.</param>
        private bool CheckAndAddItemModifications(CdmDocumentDefinition document)
        {
            if (this.Item(document.Name) != null)
            {
                Logger.Error(this.Ctx, Tag, nameof(CheckAndAddItemModifications), document.AtCorpusPath, CdmLogCode.ErrDocAlreadyExist, document.Name,
                    this.Owner.AtCorpusPath != null ? this.Owner.AtCorpusPath : this.Owner.Name);
                return false;
            }

            if (document.Owner != null && document.Owner != this.Owner)
            {
                // this is fun! the document is moving from one folder to another
                // it must be removed from the old folder for sure, but also now 
                // there will be a problem with any corpus paths that are relative to that old folder location.
                // so, whip through the document and change any corpus paths to be relative to this folder
                document.LocalizeCorpusPaths(this.Owner); // returns false if it fails, but ... who cares? we tried
                (document.Owner as CdmFolderDefinition).Documents.Remove(document.Name);
            }

            document.FolderPath = this.Owner.FolderPath;
            document.Owner = this.Owner;
            document.Namespace = this.Owner.Namespace;
            MakeDocumentDirty(); // set the document to dirty so it will get saved in the new folder location if saved
            this.Owner.Corpus.AddDocumentObjects(this.Owner, document);
            return true;
        }

        /// <summary>
        /// Performs changes associated with removing an item from the collection.
        /// Does not actually remove the item from the collection.
        /// </summary>
        /// <param name="documentName">The name of the document that is to be removed.</param>
        private void RemoveItemModifications(string documentName)
        {
            this.Owner.Corpus.RemoveDocumentObjects(this.Owner, this.Owner.DocumentLookup[documentName]);
            this.Owner.DocumentLookup.Remove(documentName);
        }
    }
}
