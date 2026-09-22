/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Stable public Research API error codes.
 *
 * 错误码值与领域服务异常的 .code 属性保持一致，
 * API 层据此构造 ResearchErrorResponse 返回给客户端。
 */
export enum ResearchErrorCode {
    INSTRUMENT_NOT_FOUND = 'INSTRUMENT_NOT_FOUND',
    RESEARCH_PACKAGE_NOT_FOUND = 'RESEARCH_PACKAGE_NOT_FOUND',
    RESEARCH_PACKAGE_ALREADY_EXISTS = 'RESEARCH_PACKAGE_ALREADY_EXISTS',
    RESEARCH_VERSION_CONFLICT = 'RESEARCH_VERSION_CONFLICT',
    IDEMPOTENCY_CONFLICT = 'IDEMPOTENCY_CONFLICT',
    RESEARCH_VALIDATION_ERROR = 'RESEARCH_VALIDATION_ERROR',
    RESEARCH_PERSISTENCE_CONFLICT = 'RESEARCH_PERSISTENCE_CONFLICT',
    RESEARCH_DOMAIN_ERROR = 'RESEARCH_DOMAIN_ERROR',
}
