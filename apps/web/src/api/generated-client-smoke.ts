import {
  ApiError,
  ResearchService,
  ResearchErrorCode,
  ResearchFreshness,
  type ApiResult,
  type HTTPValidationError,
  type ResearchErrorResponse,
  ResearchModuleType,
  type ResearchPackageRead,
  type ResearchRefreshRequest,
} from './generated'
import type { AxiosInstance } from 'axios'
import {
  apiClient,
  isResearchApiErrorForStatus,
  reportApiErrorAndRethrow,
  type ResearchApiErrorBody,
  type ResearchApiErrorBodyForStatus,
} from './client'

type IsAny<T> = 0 extends (1 & T) ? true : false
type AssertFalse<T extends false> = T
type AssertTrue<T extends true> = T
type IsNever<T> = [T] extends [never] ? true : false

const validFreshness: ResearchFreshness = ResearchFreshness.FRESH
const compatibleClient: AxiosInstance = apiClient

// @ts-expect-error ResearchFreshness must stay limited to the OpenAPI enum.
const invalidFreshness: ResearchFreshness = 'UNKNOWN'

const refreshBody: ResearchRefreshRequest = {
  expected_version: 1,
  module_types: [ResearchModuleType.FINANCIAL],
}

type CreateInitialResearchOptions = Parameters<
  typeof ResearchService.createInitialResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesPost
>[0]

type RefreshResearchOptions = Parameters<
  typeof ResearchService.refreshResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesRefreshPost
>[0]

type GeneratedApiErrorBodyIsNotAny = AssertFalse<IsAny<ApiError['body']>>
type CreateInitial422ErrorIsNotAny = AssertFalse<IsAny<ResearchApiErrorBodyForStatus<'createInitial', 422>>>
type Refresh422ErrorIsNotAny = AssertFalse<IsAny<ResearchApiErrorBodyForStatus<'refresh', 422>>>
type Version422ErrorIsNotAny = AssertFalse<IsAny<ResearchApiErrorBodyForStatus<'getVersion', 422>>>
type CreateInitial422IncludesResearchError = AssertFalse<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'createInitial', 422>, ResearchErrorResponse>>
>
type CreateInitial422IncludesHTTPValidationError = AssertFalse<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'createInitial', 422>, HTTPValidationError>>
>
type Refresh422IncludesResearchError = AssertFalse<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'refresh', 422>, ResearchErrorResponse>>
>
type Refresh422IncludesHTTPValidationError = AssertFalse<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'refresh', 422>, HTTPValidationError>>
>
type Version422DoesNotIncludeResearchError = AssertTrue<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'getVersion', 422>, ResearchErrorResponse>>
>
type Version404IncludesResearchError = AssertFalse<
  IsNever<Extract<ResearchApiErrorBodyForStatus<'getVersion', 404>, ResearchErrorResponse>>
>
type Create409ErrorIsResearchError = AssertTrue<
  ResearchApiErrorBodyForStatus<'createInitial', 409> extends ResearchErrorResponse ? true : false
>
type Refresh409ErrorIsResearchError = AssertTrue<
  ResearchApiErrorBodyForStatus<'refresh', 409> extends ResearchErrorResponse ? true : false
>
type ResearchErrorBodyIsGeneratedModels = AssertTrue<
  ResearchApiErrorBody<'createInitial'> extends ResearchErrorResponse | HTTPValidationError ? true : false
>

// @ts-expect-error Idempotency-Key is required by the generated create operation.
const missingCreateIdempotencyKey: CreateInitialResearchOptions = {
  instrumentId: '11111111-1111-4111-8111-111111111111',
}

// @ts-expect-error Idempotency-Key is required by the generated refresh operation.
const missingRefreshIdempotencyKey: RefreshResearchOptions = {
  instrumentId: '11111111-1111-4111-8111-111111111111',
  requestBody: refreshBody,
}

function acceptResearchPackage(packageRead: ResearchPackageRead): string {
  return packageRead.id
}

function acceptCreateInitial422Error(
  error: ResearchApiErrorBodyForStatus<'createInitial', 422>,
): ResearchApiErrorBodyForStatus<'createInitial', 422> {
  return error
}

function acceptVersion422Error(
  error: ResearchApiErrorBodyForStatus<'getVersion', 422>,
): ResearchApiErrorBodyForStatus<'getVersion', 422> {
  return error
}

function buildApiError<TBody>(status: number, body: TBody): ApiError<TBody> {
  const result: ApiResult<TBody> = {
    url: '/api/v1/research/instruments/example/packages',
    ok: false,
    status,
    statusText: 'Conflict',
    body,
  }
  return new ApiError<TBody>(
    {
      method: 'POST',
      url: '/api/v1/research/instruments/{instrument_id}/packages',
    },
    result,
    'Research conflict',
  )
}

async function smokeResearchClient(): Promise<void> {
  const created = await ResearchService.createInitialResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesPost(
    {
      instrumentId: '11111111-1111-4111-8111-111111111111',
      idempotencyKey: 'client-smoke-create',
    },
  )
  acceptResearchPackage(created)

  const current = await ResearchService.getCurrentResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesCurrentGet(
    {
      instrumentId: '11111111-1111-4111-8111-111111111111',
    },
  )
  acceptResearchPackage(current)

  const history = await ResearchService.listResearchPackageHistoryEndpointApiV1ResearchInstrumentsInstrumentIdPackagesGet(
    {
      instrumentId: '11111111-1111-4111-8111-111111111111',
    },
  )
  history.forEach(acceptResearchPackage)

  const version = await ResearchService.getResearchPackageVersionEndpointApiV1ResearchInstrumentsInstrumentIdPackagesVersionsVersionGet(
    {
      instrumentId: '11111111-1111-4111-8111-111111111111',
      version: 1,
    },
  )
  acceptResearchPackage(version)

  const refreshed = await ResearchService.refreshResearchPackageEndpointApiV1ResearchInstrumentsInstrumentIdPackagesRefreshPost(
    {
      instrumentId: '11111111-1111-4111-8111-111111111111',
      idempotencyKey: 'client-smoke-refresh',
      requestBody: refreshBody,
    },
  )
  acceptResearchPackage(refreshed)

  acceptCreateInitial422Error({
    detail: {
      code: ResearchErrorCode.RESEARCH_VALIDATION_ERROR,
      message: 'Idempotency-Key must not be blank',
    },
  })
  acceptCreateInitial422Error({
    detail: [
      {
        loc: ['header', 'Idempotency-Key'],
        msg: 'Field required',
        type: 'missing',
      },
    ],
  })
  acceptVersion422Error({
    detail: [
      {
        loc: ['path', 'version'],
        msg: 'Input should be greater than or equal to 1',
        type: 'greater_than_equal',
      },
    ],
  })

  const conflictError = buildApiError<ResearchApiErrorBodyForStatus<'createInitial', 409>>(
    409,
    {
      detail: {
        code: ResearchErrorCode.RESEARCH_PACKAGE_ALREADY_EXISTS,
        message: 'Research Package already exists',
      },
    },
  )
  if (isResearchApiErrorForStatus(conflictError, 'createInitial', 409)) {
    const code: ResearchErrorCode = conflictError.body.detail.code
    void code
  }

  try {
    reportApiErrorAndRethrow(conflictError)
  } catch (error: unknown) {
    if (isResearchApiErrorForStatus(error, 'createInitial', 409)) {
      const message: string = error.body.detail.message
      void message
    }
  }
}

void validFreshness
void invalidFreshness
void missingCreateIdempotencyKey
void missingRefreshIdempotencyKey
void smokeResearchClient
void compatibleClient
void (undefined as unknown as GeneratedApiErrorBodyIsNotAny)
void (undefined as unknown as CreateInitial422ErrorIsNotAny)
void (undefined as unknown as Refresh422ErrorIsNotAny)
void (undefined as unknown as Version422ErrorIsNotAny)
void (undefined as unknown as CreateInitial422IncludesResearchError)
void (undefined as unknown as CreateInitial422IncludesHTTPValidationError)
void (undefined as unknown as Refresh422IncludesResearchError)
void (undefined as unknown as Refresh422IncludesHTTPValidationError)
void (undefined as unknown as Version422DoesNotIncludeResearchError)
void (undefined as unknown as Version404IncludesResearchError)
void (undefined as unknown as Create409ErrorIsResearchError)
void (undefined as unknown as Refresh409ErrorIsResearchError)
void (undefined as unknown as ResearchErrorBodyIsGeneratedModels)
