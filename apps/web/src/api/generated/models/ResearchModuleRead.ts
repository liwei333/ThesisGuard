/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResearchFreshness } from './ResearchFreshness';
/**
 * Research module snapshot response schema.
 */
export type ResearchModuleRead = {
    as_of: string;
    created_at: string;
    /**
     * Deterministic content freshness. UNVERIFIED means no source-backed verification exists; FRESH/STALE are derived from last_verified_at and stale_after; FAILED means module refresh failed.
     */
    freshness: ResearchFreshness;
    id: string;
    last_verified_at?: (string | null);
    module_type: string;
    module_version: number;
    origin_module_id?: (string | null);
    research_package_id: string;
    source_refs: Array<string>;
    stale_after: string;
    status: string;
    summary?: (string | null);
};
