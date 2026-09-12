/**
 * ThesisGuard API Client
 *
 * Centralized API client. All API calls go through this module.
 * Never hand-write URLs in components.
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'

// Create axios instance with defaults
const client: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/${API_VERSION}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log error for debugging; can be extended for toast notifications
    console.error('[API Error]', error.response?.status, error.message)
    return Promise.reject(error)
  },
)

// ============================================================
// Health endpoints
// ============================================================

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await client.get<HealthResponse>('/health')
  return data
}

// ============================================================
// System status endpoints
// ============================================================

export interface ServiceStatus {
  status: string
  message: string
}

export interface SystemStatusResponse {
  status: string
  api: { status: string; version: string }
  services: {
    postgres: ServiceStatus
    redis: ServiceStatus
    object_storage: ServiceStatus
    worker: ServiceStatus
  }
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  const { data } = await client.get<SystemStatusResponse>('/system/status')
  return data
}

// ============================================================
// Task endpoints
// ============================================================

export interface TaskDispatchResponse {
  task_id: string
  actor: string
  status: string
  message: string
}

export async function dispatchHealthCheckTask(): Promise<TaskDispatchResponse> {
  const { data } = await client.post<TaskDispatchResponse>('/tasks/health-check')
  return data
}

export async function dispatchEchoTask(
  message: string,
): Promise<TaskDispatchResponse> {
  const { data } = await client.post<TaskDispatchResponse>('/tasks/echo', {
    message,
  })
  return data
}

// Export the raw client for advanced use cases
export { client as apiClient }
