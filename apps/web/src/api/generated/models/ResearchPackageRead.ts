/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResearchModuleRead } from './ResearchModuleRead';
/**
 * Research package version response schema.
 *
 * Package status is a build lifecycle state. Module freshness is the content
 * freshness signal. PENDING or UNVERIFIED content is not ACTIVE verified
 * research, and stale content must not be silently displayed as current.
 */
export type ResearchPackageRead = {
    as_of: string;
    completed_at?: (string | null);
    created_at: string;
    expected_version?: (number | null);
    id: string;
    instrument_id: string;
    last_verified_at?: (string | null);
    modules: Array<ResearchModuleRead>;
    previous_version_id?: (string | null);
    started_at: string;
    /**
     * Build lifecycle status for the package version, not a content freshness verdict. PENDING does not mean ACTIVE verified research.
     */
    status: string;
    trigger_type: string;
    version: number;
};
