/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WatchlistAddRequest } from '../models/WatchlistAddRequest';
import type { WatchlistItemRead } from '../models/WatchlistItemRead';
import type { WatchlistUpdateRequest } from '../models/WatchlistUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WatchlistService {
    /**
     * List Watchlist Endpoint
     * List watchlist items.
     * @returns WatchlistItemRead Successful Response
     * @throws ApiError
     */
    public static listWatchlistEndpointApiV1WatchlistGet({
        classification,
    }: {
        classification?: (string | null),
    }): CancelablePromise<Array<WatchlistItemRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/watchlist',
            query: {
                'classification': classification,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Watchlist Endpoint
     * Add an instrument to watchlist and classify it.
     * @returns WatchlistItemRead Successful Response
     * @throws ApiError
     */
    public static addWatchlistEndpointApiV1WatchlistPost({
        requestBody,
    }: {
        requestBody: WatchlistAddRequest,
    }): CancelablePromise<WatchlistItemRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/watchlist',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Watchlist Endpoint
     * Delete a watchlist item.
     * @returns void
     * @throws ApiError
     */
    public static deleteWatchlistEndpointApiV1WatchlistItemIdDelete({
        itemId,
    }: {
        itemId: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/watchlist/{item_id}',
            path: {
                'item_id': itemId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Watchlist Endpoint
     * Update a watchlist item.
     * @returns WatchlistItemRead Successful Response
     * @throws ApiError
     */
    public static updateWatchlistEndpointApiV1WatchlistItemIdPatch({
        itemId,
        requestBody,
    }: {
        itemId: string,
        requestBody: WatchlistUpdateRequest,
    }): CancelablePromise<WatchlistItemRead> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/watchlist/{item_id}',
            path: {
                'item_id': itemId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
