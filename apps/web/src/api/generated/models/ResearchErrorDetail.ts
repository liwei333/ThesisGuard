/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResearchErrorCode } from './ResearchErrorCode';
/**
 * Stable public Research API error detail.
 */
export type ResearchErrorDetail = {
    code: ResearchErrorCode;
    current_version?: (number | null);
    expected_version?: (number | null);
    message: string;
};
