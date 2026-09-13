/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SystemStatusResponse } from '../models/SystemStatusResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SystemService {
    /**
     * System Status
     * Comprehensive system status check.
     *
     * Returns status of all core services: postgres, redis, object_storage, worker.
     * @returns SystemStatusResponse Successful Response
     * @throws ApiError
     */
    public static systemStatusApiV1SystemStatusGet(): CancelablePromise<SystemStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/system/status',
        });
    }
    /**
     * Postgres Status
     * PostgreSQL specific status.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static postgresStatusApiV1SystemStatusPostgresGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/system/status/postgres',
        });
    }
    /**
     * Redis Status
     * Redis specific status.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static redisStatusApiV1SystemStatusRedisGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/system/status/redis',
        });
    }
    /**
     * Storage Status
     * MinIO/Object Storage specific status.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static storageStatusApiV1SystemStatusStorageGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/system/status/storage',
        });
    }
}
