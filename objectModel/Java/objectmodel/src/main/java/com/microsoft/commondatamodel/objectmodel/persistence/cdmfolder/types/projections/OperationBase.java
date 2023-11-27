// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

package com.microsoft.commondatamodel.objectmodel.persistence.cdmfolder.types.projections;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

/**
 * OperationBase class
 */
@JsonPropertyOrder({"$type"})
public class OperationBase {
    @JsonProperty("$type")
    private String type;
    private String condition;
    private String explanation;
    private Boolean sourceInput;

    public String getType() {
        return type;
    }

    /**
     * @deprecated This function is extremely likely to be removed in the public interface, and not
     * meant to be called externally at all. Please refrain from using it.
     * @param type String
     */
    @Deprecated
    public void setType(final String type) {
        this.type = type;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(final String explanation) {
        this.explanation = explanation;
    }

    public String getCondition() {
        return condition;
    }

    public void setCondition(String condition) {
        this.condition = condition;
    }

    public Boolean getSourceInput() {
        return sourceInput;
    }

    public void setSourceInput(Boolean sourceInput) {
        this.sourceInput = sourceInput;
    }
}
