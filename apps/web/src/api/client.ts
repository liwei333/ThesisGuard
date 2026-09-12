/**
 * ThesisGuard API Client
 *
 * Centralized API client. All API calls go through this module.
 * Never hand-write URLs in components.
 */

import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'
const normalizedBaseUrl = API_BASE_URL.replace(/\/$/, '')
const versionedBaseUrl = normalizedBaseUrl.endsWith('/api')
  ? `${normalizedBaseUrl}/${API_VERSION}`
  : `${normalizedBaseUrl}/api/${API_VERSION}`

// Create axios instance with defaults
const client: AxiosInstance = axios.create({
  baseURL: versionedBaseUrl,
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

// ============================================================
// Instrument + Watchlist endpoints
// ============================================================

export interface Instrument {
  id: string
  symbol: string
  name: string
  instrument_type: string
  exchange: string
  market: string
  currency: string
  sector?: string | null
  industry?: string | null
  description?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface WatchlistItem {
  id: string
  instrument_id: string
  instrument: Instrument
  classification: string
  classification_confidence: number
  classification_reason: string
  research_status: string
  research_score?: number | null
  thesis_summary?: string | null
  agent_action?: string | null
  notes?: string | null
  created_at: string
  updated_at: string
}

export async function searchInstruments(query: string): Promise<Instrument[]> {
  const { data } = await client.get<Instrument[]>('/instruments/search', {
    params: { query },
  })
  return data
}

export async function listWatchlist(): Promise<WatchlistItem[]> {
  const { data } = await client.get<WatchlistItem[]>('/watchlist')
  return data
}

export async function addWatchlistItem(
  query: string,
): Promise<WatchlistItem> {
  const { data } = await client.post<WatchlistItem>('/watchlist', { query })
  return data
}

export async function deleteWatchlistItem(itemId: string): Promise<void> {
  await client.delete(`/watchlist/${itemId}`)
}

// Export the raw client for advanced use cases
export { client as apiClient }
