/**
 * ThesisGuard API facade.
 *
 * Manual code in this file is limited to generated-client configuration,
 * compatibility exports, and stable application-level function names.
 *
 * 前端 API 客户端外观层。封装自动生成的 OpenAPI 客户端，提供：
 * 1. 稳定的应用级函数命名（如 searchInstruments 而非生成的长名）
 * 2. Research 错误类型守卫（isResearchApiError / isResearchApiErrorForStatus）
 * 3. 统一的错误日志和重抛（reportApiErrorAndRethrow）
 *
 * 注意：不要在此文件中手写业务端点 URL，所有路径由 generated 目录提供。
 */

import axios from 'axios'
import type { AxiosInstance } from 'axios'
import {
  ApiError,
  HealthService,
  InstrumentService,
  OpenAPI,
  ResearchErrorCode as GeneratedResearchErrorCode,
  ResearchService,
  SystemService,
  TasksService,
  WatchlistService,
  type HealthResponse,
  type HTTPValidationError,
  type InstrumentRead,
  type ResearchErrorCode,
  type ResearchErrorDetail,
  type ResearchErrorResponse,
  type ResearchFreshness,
  type ResearchModuleRead,
  type ResearchModuleType,
  type ResearchPackageRead,
  type ResearchRefreshRequest,
  type SystemStatusResponse,
  type TaskDispatchResponse,
  type ValidationError,
  type WatchlistItemRead,
} from './generated'

const REQUEST_TIMEOUT_MS = 30000

function normalizeApiBaseUrl(baseUrl: string | undefined): string {
  return (baseUrl ?? '').replace(/\/$/, '')
}

OpenAPI.BASE = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL)
export const apiClient: AxiosInstance = axios.create({
  baseURL: OpenAPI.BASE,
  timeout: REQUEST_TIMEOUT_MS,
})
OpenAPI.AXIOS = apiClient

// Research 操作的错误契约：定义每个操作在各状态码下的错误响应类型
// 用于运行时类型守卫，确保错误处理分支覆盖所有已声明的状态码
type ResearchErrorContract = {
  listHistory: {
    422: HTTPValidationError
  }
  getCurrent: {
    404: ResearchErrorResponse
    422: HTTPValidationError
  }
  getVersion: {
    404: ResearchErrorResponse
    422: HTTPValidationError
  }
  createInitial: {
    404: ResearchErrorResponse
    409: ResearchErrorResponse
    // 422 可能是领域验证错误或 FastAPI 请求验证错误
    422: ResearchErrorResponse | HTTPValidationError
  }
  refresh: {
    404: ResearchErrorResponse
    409: ResearchErrorResponse
    422: ResearchErrorResponse | HTTPValidationError
  }
}

export type ResearchOperation = keyof ResearchErrorContract
export type ResearchApiErrorBody<TOperation extends ResearchOperation> =
  ResearchErrorContract[TOperation][keyof ResearchErrorContract[TOperation]]
export type ResearchApiErrorBodyForStatus<
  TOperation extends ResearchOperation,
  TStatus extends keyof ResearchErrorContract[TOperation],
> = ResearchErrorContract[TOperation][TStatus]
export type ResearchApiError<TOperation extends ResearchOperation> = ApiError<
  ResearchApiErrorBody<TOperation>
>
export type ResearchApiPromise<
  TSuccess,
  TOperation extends ResearchOperation,
> = Promise<TSuccess> & {
  readonly __researchErrorBody?: ResearchApiErrorBody<TOperation>
}

type ResearchStatusForOperation<TOperation extends ResearchOperation> =
  keyof ResearchErrorContract[TOperation] & number

const researchErrorStatuses = {
  listHistory: [422],
  getCurrent: [404, 422],
  getVersion: [404, 422],
  createInitial: [404, 409, 422],
  refresh: [404, 409, 422],
} as const satisfies Record<ResearchOperation, readonly number[]>

const researchErrorCodeValues = new Set<string>(
  Object.values(GeneratedResearchErrorCode),
)

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isResearchErrorCode(value: unknown): value is ResearchErrorCode {
  return typeof value === 'string' && researchErrorCodeValues.has(value)
}

function isOptionalIntegerOrNull(
  value: unknown,
): value is number | null | undefined {
  return value === undefined || value === null || Number.isInteger(value)
}

function isResearchErrorResponse(value: unknown): value is ResearchErrorResponse {
  if (!isRecord(value) || !isRecord(value.detail)) {
    return false
  }
  return (
    isResearchErrorCode(value.detail.code) &&
    typeof value.detail.message === 'string' &&
    isOptionalIntegerOrNull(value.detail.expected_version) &&
    isOptionalIntegerOrNull(value.detail.current_version)
  )
}

function isValidationLocationItem(value: unknown): value is string | number {
  return typeof value === 'string' || Number.isInteger(value)
}

function isValidationError(value: unknown): value is ValidationError {
  if (
    !isRecord(value) ||
    !Array.isArray(value.loc) ||
    typeof value.msg !== 'string' ||
    typeof value.type !== 'string'
  ) {
    return false
  }
  return (
    value.loc.every(isValidationLocationItem) &&
    (value.ctx === undefined || isRecord(value.ctx))
  )
}

function isHTTPValidationError(value: unknown): value is HTTPValidationError {
  if (!isRecord(value)) {
    return false
  }
  if (value.detail === undefined) {
    return true
  }
  return Array.isArray(value.detail) && value.detail.every(isValidationError)
}

function isResearchErrorBodyForOperationStatus(
  operation: ResearchOperation,
  status: number,
  body: unknown,
): boolean {
  if (status === 404 || status === 409) {
    return isResearchErrorResponse(body)
  }
  if (status !== 422) {
    return false
  }
  if (operation === 'createInitial' || operation === 'refresh') {
    return isResearchErrorResponse(body) || isHTTPValidationError(body)
  }
  return isHTTPValidationError(body)
}

function isDeclaredResearchStatus(
  operation: ResearchOperation,
  status: number,
): boolean {
  return (researchErrorStatuses[operation] as readonly number[]).includes(status)
}

export function isResearchApiErrorForStatus<
  TOperation extends ResearchOperation,
  TStatus extends ResearchStatusForOperation<TOperation>,
>(
  error: unknown,
  operation: TOperation,
  status: TStatus,
): error is ApiError<ResearchApiErrorBodyForStatus<TOperation, TStatus>> & {
  readonly status: TStatus
} {
  return (
    error instanceof ApiError &&
    error.status === status &&
    isDeclaredResearchStatus(operation, status) &&
    isResearchErrorBodyForOperationStatus(operation, status, error.body)
  )
}

export function isResearchApiError<TOperation extends ResearchOperation>(
  error: unknown,
  operation: TOperation,
): error is ResearchApiError<TOperation> {
  return (
    error instanceof ApiError &&
    isDeclaredResearchStatus(operation, error.status) &&
    isResearchErrorBodyForOperationStatus(operation, error.status, error.body)
  )
}

function getApiErrorStatus(error: unknown): number | undefined {
  if (axios.isAxiosError(error)) {
    return error.response?.status
  }
  if (error instanceof ApiError) {
    return error.status
  }
  return undefined
}

export function reportApiErrorAndRethrow(error: unknown): never {
  const message = error instanceof Error ? error.message : 'Unknown API error'
  console.error('[API Error]', getApiErrorStatus(error), message)
  throw error
}

async function withApiLogging<T>(operation: Promise<T>): Promise<T> {
  try {
    return await operation
  } catch (error: unknown) {
    reportApiErrorAndRethrow(error)
  }
}

export type {
  HealthResponse,
  HTTPValidationError,
  ResearchErrorCode,
  ResearchErrorDetail,
  ResearchErrorResponse,
  ResearchFreshness,
  ResearchModuleRead,
  ResearchModuleType,
  ResearchPackageRead,
  ResearchRefreshRequest,
  SystemStatusResponse,
  TaskDispatchResponse,
  ValidationError,
}

export type Instrument = InstrumentRead
export type WatchlistItem = WatchlistItemRead

export async function getHealth(): Promise<HealthResponse> {
  return withApiLogging(HealthService.healthCheckApiV1HealthGet())
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  return withApiLogging(SystemService.systemStatusApiV1SystemStatusGet())
}

export async function dispatchHealthCheckTask(): Promise<TaskDispatchResponse> {
  return withApiLogging(TasksService.dispatchHealthCheckApiV1TasksHealthCheckPost())
}

export async function dispatchEchoTask(
  message: string,
): Promise<TaskDispatchResponse> {
  return withApiLogging(
    TasksService.dispatchEchoApiV1TasksEchoPost({
      requestBody: { message },
    }),
  )
}

export async function searchInstruments(query: string): Promise<Instrument[]> {
  return withApiLogging(
    InstrumentService.searchInstrumentEndpointApiV1InstrumentsSearchGet({ query }),
  )
}

export async function listWatchlist(): Promise<WatchlistItem[]> {
  return withApiLogging(
    WatchlistService.listWatchlistEndpointApiV1WatchlistGet({}),
  )
}

export async function addWatchlistItem(query: string): Promise<WatchlistItem> {
  return withApiLogging(
    WatchlistService.addWatchlistEndpointApiV1WatchlistPost({
      requestBody: { query },
    }),
  )
}

export async function deleteWatchlistItem(itemId: string): Promise<void> {
  await withApiLogging(
    WatchlistService.deleteWatchlistEndpointApiV1WatchlistItemIdDelete({ itemId }),
  )
}

export function createInitialResearchPackage(
  instrumentId: string,
  idempotencyKey: string,
): ResearchApiPromise<ResearchPackageRead, 'createInitial'> {
  return withApiLogging(
    ResearchService.createInitialResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesPost({
      instrumentId,
      idempotencyKey,
    }),
  )
}

export function getCurrentResearchPackage(
  instrumentId: string,
): ResearchApiPromise<ResearchPackageRead, 'getCurrent'> {
  return withApiLogging(
    ResearchService.getCurrentResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesCurrentGet({
      instrumentId,
    }),
  )
}

export function listResearchPackageHistory(
  instrumentId: string,
): ResearchApiPromise<ResearchPackageRead[], 'listHistory'> {
  return withApiLogging(
    ResearchService.listResearchPackageHistoryEndpointApiV1ResearchInstrumentsInstrumentIdPackagesGet({
      instrumentId,
    }),
  )
}

export function getResearchPackageVersion(
  instrumentId: string,
  version: number,
): ResearchApiPromise<ResearchPackageRead, 'getVersion'> {
  return withApiLogging(
    ResearchService.getResearchPackageVersionEndpointApiV1ResearchInstrumentsInstrumentIdPackagesVersionsVersionGet({
      instrumentId,
      version,
    }),
  )
}

export function refreshResearchPackage(
  instrumentId: string,
  idempotencyKey: string,
  requestBody: ResearchRefreshRequest,
): ResearchApiPromise<ResearchPackageRead, 'refresh'> {
  return withApiLogging(
    ResearchService.refreshResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesRefreshPost({
      instrumentId,
      idempotencyKey,
      requestBody,
    }),
  )
}

export { OpenAPI as openApiConfig }
