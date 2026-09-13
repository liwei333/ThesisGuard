/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResearchPackageRead } from '../models/ResearchPackageRead';
import type { ResearchRefreshRequest } from '../models/ResearchRefreshRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResearchService {
    /**
     * List Research Package History Endpoint
     * List all Research Package versions for an instrument.
     * @returns ResearchPackageRead Successful Response
     * @throws ApiError
     */
    public static listResearchPackageHistoryEndpointApiV1ResearchInstrumentsInstrumentIdPackagesGet({
        instrumentId,
    }: {
        instrumentId: string,
    }): CancelablePromise<Array<ResearchPackageRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/research/instruments/{instrument_id}/packages',
            path: {
                'instrument_id': instrumentId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Initial Research Package Endpoint
     * Create initial Research Package version 1 for an instrument.
     * @returns ResearchPackageRead Successful Response
     * @throws ApiError
     */
    public static createInitialResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesPost({
        instrumentId,
        idempotencyKey,
    }: {
        instrumentId: string,
        /**
         * Required idempotency key for Research Package mutations.
         */
        idempotencyKey: string,
    }): CancelablePromise<ResearchPackageRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/research/instruments/{instrument_id}/packages',
            path: {
                'instrument_id': instrumentId,
            },
            headers: {
                'Idempotency-Key': idempotencyKey,
            },
            errors: {
                404: `Research resource not found`,
                409: `Research write, version, or idempotency conflict`,
                422: `FastAPI request validation or Research domain validation error`,
            },
        });
    }
    /**
     * Get Current Research Package Endpoint
     * Get the current Research Package version for an instrument.
     * @returns ResearchPackageRead Successful Response
     * @throws ApiError
     */
    public static getCurrentResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesCurrentGet({
        instrumentId,
    }: {
        instrumentId: string,
    }): CancelablePromise<ResearchPackageRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/research/instruments/{instrument_id}/packages/current',
            path: {
                'instrument_id': instrumentId,
            },
            errors: {
                404: `Research resource not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Refresh Research Package Endpoint
     * Create an append-only incremental Research Package version.
     * @returns ResearchPackageRead Successful Response
     * @throws ApiError
     */
    public static refreshResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesRefreshPost({
        instrumentId,
        idempotencyKey,
        requestBody,
    }: {
        instrumentId: string,
        /**
         * Required idempotency key for Research Package mutations.
         */
        idempotencyKey: string,
        requestBody: ResearchRefreshRequest,
    }): CancelablePromise<ResearchPackageRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/research/instruments/{instrument_id}/packages/refresh',
            path: {
                'instrument_id': instrumentId,
            },
            headers: {
                'Idempotency-Key': idempotencyKey,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Research resource not found`,
                409: `Research write, version, or idempotency conflict`,
                422: `FastAPI request validation or Research domain validation error`,
            },
        });
    }
    /**
     * Get Research Package Version Endpoint
     * Get a specified Research Package version for an instrument.
     * @returns ResearchPackageRead Successful Response
     * @throws ApiError
     */
    public static getResearchPackageVersionEndpointApiV1ResearchInstrumentsInstrumentIdPackagesVersionsVersionGet({
        instrumentId,
        version,
    }: {
        instrumentId: string,
        version: number,
    }): CancelablePromise<ResearchPackageRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/research/instruments/{instrument_id}/packages/versions/{version}',
            path: {
                'instrument_id': instrumentId,
                'version': version,
            },
            errors: {
                404: `Research resource not found`,
                422: `FastAPI request validation error`,
            },
        });
    }
}
