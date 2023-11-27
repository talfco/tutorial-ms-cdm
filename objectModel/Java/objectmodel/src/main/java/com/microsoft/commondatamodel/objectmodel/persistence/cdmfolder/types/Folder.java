// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

package com.microsoft.commondatamodel.objectmodel.persistence.cdmfolder.types;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;

/**
 * The folder for CDM folder format.
 */
public class Folder {
    private String folderName;
    private String explanation;
    private JsonNode exhibitsTraits;

    /**
     * Gets the folder name.
     * @return String
     */
    public String getFolderName() {
        return folderName;
    }

    /**
     * Sets the folder name.
     * @param folderName String
     */
    public void setFolderName(final String folderName) {
        this.folderName = folderName;
    }

    /**
     * Gets the folder explanation.
     * @return String
     */
    public String getExplanation() {
        return explanation;
    }

    /**
     * Sets the folder explanation.
     * @param explanation String
     */
    public void setExplanation(final String explanation) {
        this.explanation = explanation;
    }

    /**
     * Gets the exhibited traits.
     * @return JsonNode
     */
    public JsonNode getExhibitsTraits() {
        return exhibitsTraits;
    }

    /**
     * Sets the exhibited traits.
     * @param exhibitsTraits JsonNode
     */
    public void setExhibitsTraits(final JsonNode exhibitsTraits) {
        this.exhibitsTraits = exhibitsTraits;
    }
}
