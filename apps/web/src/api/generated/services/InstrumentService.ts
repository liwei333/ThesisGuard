/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InstrumentRead } from '../models/InstrumentRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class InstrumentService {
    /**
     * Search Instrument Endpoint
     * Search instruments by symbol, name, alias, or tag.
     * @returns InstrumentRead Successful Response
     * @throws ApiError
     */
    public static searchInstrumentEndpointApiV1InstrumentsSearchGet({
        query,
        limit = 10,
    }: {
        query: string,
        limit?: number,
    }): CancelablePromise<Array<InstrumentRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/instruments/search',
            query: {
                'query': query,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Instrument Endpoint
     * Get an instrument by symbol.
     * @returns InstrumentRead Successful Response
     * @throws ApiError
     */
    public static getInstrumentEndpointApiV1InstrumentsSymbolGet({
        symbol,
    }: {
        symbol: string,
    }): CancelablePromise<InstrumentRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/instruments/{symbol}',
            path: {
                'symbol': symbol,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
