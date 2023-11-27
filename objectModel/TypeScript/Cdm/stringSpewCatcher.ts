// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for license information.

import { spewCatcher } from '../internal';

/**
 * @internal
 */
export class stringSpewCatcher implements spewCatcher {
    public content : string = '';
    public segment : string = '';
    public clear(): void {
        this.content = '';
        this.segment = '';
    }
    public spewLine(spew: string): void {
        this.segment += `${spew}\n`;
        if (this.segment.length > 1000) {
            this.content += this.segment;
            this.segment = '';
        }
    }
    public getContent(): string {
        return this.content + this.segment;
    }
}
