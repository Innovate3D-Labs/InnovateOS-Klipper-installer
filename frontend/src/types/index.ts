// User Types
export interface User {
  id: string
  username: string
  email: string
  created_at: string
  updated_at: string
  preferences?: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark'
  language: string
  notifications: boolean
}

// Hardware Types
export interface Board {
  port: string
  vendor_id: string
  product_id: string
  manufacturer: string
  description: string
  serial_number: string
  detected_type?: string
}

export interface BoardConfig {
  name: string
  mcu: string
  flash_method: string
  build_flags: string[]
  supported_firmwares: string[]
}

// Installation Types
export interface Installation {
  id: string
  user_id: string
  board: Board
  config: any
  status: InstallationStatus
  progress: number
  started_at: string
  completed_at?: string
  error?: string
}

export type InstallationStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

// Configuration Types
export interface PrinterProfile {
  name: string
  description: string
  config: any
  created_at: string
  updated_at: string
}

export interface ConfigBackup {
  id: string
  name: string
  config: any
  created_at: string
}

// System Types
export interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  uptime: number
  active_installations: number
}

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  component: string
  details?: any
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// WebSocket Types
export interface WebSocketMessage {
  type: string
  data: any
}
