/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResearchModuleType } from './ResearchModuleType';
/**
 * Request to create an incremental Research Package version.
 */
export type ResearchRefreshRequest = {
    expected_version: number;
    module_types: Array<ResearchModuleType>;
};
