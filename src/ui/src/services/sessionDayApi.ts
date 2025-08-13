import api from './api'
import type { 
  CourseSessionDay, 
  CreateCourseSessionDayRequest, 
  UpdateCourseSessionDayRequest 
} from '@/types/courseSession'

export const sessionDayApi = {
  // List all session days with optional filtering
  list: async (params?: {
    start_date?: string
    end_date?: string
    location_id?: number
    skip?: number
    limit?: number
  }) => {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.append('start_date', params.start_date)
    if (params?.end_date) searchParams.append('end_date', params.end_date)
    if (params?.location_id) searchParams.append('location_id', params.location_id.toString())
    if (params?.skip) searchParams.append('skip', params.skip.toString())
    if (params?.limit) searchParams.append('limit', params.limit.toString())
    
    const url = `/v1/sessions/session-days${searchParams.toString() ? '?' + searchParams.toString() : ''}`
    const response = await api.get<CourseSessionDay[]>(url)
    return response.data
  },

  // Get session days for a specific session
  getBySessionId: async (sessionId: number): Promise<CourseSessionDay[]> => {
    const response = await api.get<CourseSessionDay[]>(`/v1/sessions/${sessionId}/days`)
    return response.data
  },

  // Get a specific session day by ID
  getById: async (sessionDayId: number): Promise<CourseSessionDay> => {
    const response = await api.get<CourseSessionDay>(`/v1/sessions/session-days/${sessionDayId}`)
    return response.data
  },

  // Create a new session day
  create: async (sessionId: number, sessionDay: CreateCourseSessionDayRequest): Promise<CourseSessionDay> => {
    const response = await api.post<CourseSessionDay>(`/v1/sessions/${sessionId}/days`, sessionDay)
    return response.data
  },

  // Update a session day
  update: async (sessionDayId: number, sessionDay: UpdateCourseSessionDayRequest): Promise<CourseSessionDay> => {
    const response = await api.put<CourseSessionDay>(`/v1/sessions/session-days/${sessionDayId}`, sessionDay)
    return response.data
  },

  // Delete a session day
  delete: async (sessionDayId: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/v1/sessions/session-days/${sessionDayId}`)
    return response.data
  }
}