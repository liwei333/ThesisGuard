/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Deterministic Research module freshness values.
 *
 * 由 calculate_module_freshness 基于状态和时间戳推导，
 * 不依赖 LLM 判断，保证结果可复现。
 */
export enum ResearchFreshness {
    UNVERIFIED = 'UNVERIFIED',
    FRESH = 'FRESH',
    STALE = 'STALE',
    FAILED = 'FAILED',
}
