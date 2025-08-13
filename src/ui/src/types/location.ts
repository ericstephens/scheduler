export interface Location {
  id: number
  location_name: string
  address?: string
  city?: string
  state_province?: string
  postal_code?: string
  active_status: boolean
  notes?: string
}

export interface CreateLocationRequest {
  location_name: string
  address?: string
  city?: string
  state_province?: string
  postal_code?: string
  notes?: string
}

export interface UpdateLocationRequest {
  location_name?: string
  address?: string
  city?: string
  state_province?: string
  postal_code?: string
  notes?: string
}

export interface LocationSearchRequest {
  name?: string
  city?: string
  active_only: boolean
}