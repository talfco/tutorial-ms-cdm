// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

namespace Microsoft.CommonDataModel.ObjectModel.Tests.Cdm.CdmCollection
{
    using Microsoft.CommonDataModel.ObjectModel.Cdm;
    using Microsoft.VisualStudio.TestTools.UnitTesting;
    using System.Collections.Generic;

    [TestClass]
    public class CdmImportCollectionTests
    {
        [TestMethod]
        public void TestCdmImportCollectionAdd()
        {
            var document = CdmCollectionHelperFunctions.GenerateManifest();
            document.IsDirty = false;
            Assert.AreEqual(false, document.IsDirty);
            var import = new CdmImport(document.Ctx, "corpusPath", "moniker");
            var addedImport = document.Imports.Add(import);

            Assert.IsTrue(document.IsDirty);
            Assert.AreEqual(1, document.Imports.Count);
            Assert.AreEqual(import, addedImport);
            Assert.AreEqual(import, document.Imports[0]);
            Assert.AreEqual("corpusPath", import.CorpusPath);
            Assert.AreEqual("moniker", import.Moniker);
            Assert.AreEqual(document.Ctx, import.Ctx);
        }

        [TestMethod]
        public void TestCdmImportCollectionAddCorpusPath()
        {
            var document = CdmCollectionHelperFunctions.GenerateManifest();
            document.IsDirty = false;
            var import = document.Imports.Add("corpusPath");

            Assert.IsTrue(document.IsDirty);
            Assert.AreEqual(1, document.Imports.Count);
            Assert.AreEqual(import, document.Imports[0]);
            Assert.AreEqual("corpusPath", import.CorpusPath);
            Assert.IsNull(import.Moniker);
            Assert.AreEqual(document.Ctx, import.Ctx);
        }

        [TestMethod]
        public void TestCdmImportCollectionAddCorpusPathAndMoniker()
        {
            var document = CdmCollectionHelperFunctions.GenerateManifest();
            document.IsDirty = false;
            var import = document.Imports.Add("corpusPath", "moniker");

            Assert.IsTrue(document.IsDirty);
            Assert.AreEqual(1, document.Imports.Count);
            Assert.AreEqual(import, document.Imports[0]);
            Assert.AreEqual("corpusPath", import.CorpusPath);
            Assert.AreEqual("moniker", import.Moniker);
            Assert.AreEqual(document.Ctx, import.Ctx);
        }

        [TestMethod]
        public void TestCdmImportCollectionAddRange()
        {
            var document = CdmCollectionHelperFunctions.GenerateManifest();
            document.IsDirty = false;
            var importList = new List<CdmImport>()
            {
                new CdmImport(document.Ctx, "CorpusPath1", "Moniker1"),
                new CdmImport(document.Ctx, "CorpusPath2", "Moniker2"),
                new CdmImport(document.Ctx, "CorpusPath3", null),
            };
            document.Imports.AddRange(importList);

            Assert.IsTrue(document.IsDirty);
            Assert.AreEqual(3, document.Imports.Count);
            Assert.AreEqual(importList[0], document.Imports[0]);
            Assert.AreEqual(importList[1], document.Imports[1]);
            Assert.AreEqual("CorpusPath1", document.Imports[0].CorpusPath);
            Assert.AreEqual("Moniker1", document.Imports.Item("CorpusPath1", "Moniker1").Moniker);
            Assert.AreEqual(document.Ctx, document.Imports.Item("CorpusPath1", "Moniker1").Ctx);
            Assert.AreEqual("CorpusPath2", document.Imports[1].CorpusPath);
            Assert.IsNull(document.Imports.Item("CorpusPath2"));
            Assert.IsNotNull(document.Imports.Item("CorpusPath2", checkMoniker: false));
            Assert.IsNull(document.Imports.Item("CorpusPath2", checkMoniker: true));
            Assert.IsNotNull(document.Imports.Item("CorpusPath2", "Moniker2", true));
            Assert.IsNotNull(document.Imports.Item("CorpusPath2", "Moniker3", false));
            Assert.AreEqual("Moniker2", document.Imports.Item("CorpusPath2", "Moniker2").Moniker);
            Assert.AreEqual(document.Ctx, document.Imports.Item("CorpusPath2", "Moniker2").Ctx);
            Assert.AreEqual(importList[2], document.Imports.Item("CorpusPath3"));
        }
    }
}
