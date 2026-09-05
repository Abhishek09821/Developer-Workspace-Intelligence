/** Mirror of the FastAPI Pydantic response schemas */

export interface HealthResponse {
  status: string
  environment: string
  version: string
}

export interface UserResponse {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export type ProjectSourceType = 'local_workspace' | 'zip_upload' | 'github_repository'

export type ProjectStatus =
  | 'created'
  | 'importing'
  | 'ready'
  | 'scanning'
  | 'analyzing'
  | 'completed'
  | 'failed'

export interface ProjectResponse {
  id: string
  owner_id: string
  name: string
  description: string | null
  source_type: ProjectSourceType
  status: ProjectStatus
  created_at: string
  updated_at: string
}

export interface ProjectListResponse {
  items: ProjectResponse[]
  total: number
}

export interface CreateProjectRequest {
  name: string
  source_type: ProjectSourceType
  description?: string
}

export interface ApiError {
  error: string
  message: string
  details: Record<string, unknown>
}
