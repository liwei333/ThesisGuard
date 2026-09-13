/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EchoRequest } from '../models/EchoRequest';
import type { TaskDispatchResponse } from '../models/TaskDispatchResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TasksService {
    /**
     * Dispatch Echo
     * Dispatch an echo task to the worker (for testing).
     * @returns TaskDispatchResponse Successful Response
     * @throws ApiError
     */
    public static dispatchEchoApiV1TasksEchoPost({
        requestBody,
    }: {
        requestBody: EchoRequest,
    }): CancelablePromise<TaskDispatchResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/tasks/echo',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Dispatch Health Check
     * Dispatch a system health check task to the worker.
     * @returns TaskDispatchResponse Successful Response
     * @throws ApiError
     */
    public static dispatchHealthCheckApiV1TasksHealthCheckPost(): CancelablePromise<TaskDispatchResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/tasks/health-check',
        });
    }
}
