/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InstrumentRead } from './InstrumentRead';
/**
 * Watchlist item response schema.
 */
export type WatchlistItemRead = {
    agent_action?: (string | null);
    classification: string;
    classification_confidence: number;
    classification_reason: string;
    created_at: string;
    id: string;
    instrument: InstrumentRead;
    instrument_id: string;
    notes?: (string | null);
    research_score?: (number | null);
    research_status: string;
    thesis_summary?: (string | null);
    updated_at: string;
};
