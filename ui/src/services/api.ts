import axios from 'axios'
import type { Instructor, CreateInstructorRequest, UpdateInstructorRequest, InstructorStats } from '@/types/instructor'
import type { Course, CreateCourseRequest, UpdateCourseRequest, CourseSearchRequest } from '@/types/course'
import type { CourseSession, CreateCourseSessionRequest, UpdateCourseSessionRequest, SessionSearchRequest, SessionStatus } from '@/types/courseSession'
import type { Location, CreateLocationRequest, UpdateLocationRequest, LocationSearchRequest } from '@/types/location'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens (future use)
api.interceptors.request.use((config) => {
  // Add auth token when implemented
  // const token = localStorage.getItem('token')
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`
  // }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      console.warn('Unauthorized access')
    }
    return Promise.reject(error)
  }
)

export const instructorApi = {
  // Get all instructors
  getAll: async (activeOnly = true): Promise<Instructor[]> => {
    const response = await api.get('/instructors/', {
      params: { active_only: activeOnly }
    })
    return response.data
  },

  // Get instructor by ID
  getById: async (id: number): Promise<Instructor> => {
    const response = await api.get(`/instructors/${id}`)
    return response.data
  },

  // Create new instructor
  create: async (data: CreateInstructorRequest): Promise<Instructor> => {
    const response = await api.post('/instructors/', data)
    return response.data
  },

  // Update instructor
  update: async (id: number, data: UpdateInstructorRequest): Promise<Instructor> => {
    const response = await api.put(`/instructors/${id}`, data)
    return response.data
  },

  // Update instructor status (activate/deactivate)
  updateStatus: async (id: number, active: boolean): Promise<{ message: string }> => {
    const response = await api.patch(`/instructors/${id}/status`, { active })
    return response.data
  },

  // Delete instructor (soft delete by setting active to false)
  delete: async (id: number): Promise<{ message: string }> => {
    return instructorApi.updateStatus(id, false)
  },

  // Get instructor stats
  getStats: async (id: number): Promise<InstructorStats> => {
    const response = await api.get(`/instructors/${id}/stats`)
    return response.data
  },

  // Search instructors
  search: async (query: string): Promise<Instructor[]> => {
    const response = await api.get('/instructors/search', {
      params: { q: query }
    })
    return response.data
  },
}

export const courseApi = {
  // Get all courses
  getAll: async (activeOnly = true): Promise<Course[]> => {
    const response = await api.get('/courses/', {
      params: { active_only: activeOnly }
    })
    return response.data
  },

  // Get course by ID
  getById: async (id: number): Promise<Course> => {
    const response = await api.get(`/courses/${id}`)
    return response.data
  },

  // Get course by code
  getByCode: async (code: string): Promise<Course> => {
    const response = await api.get(`/courses/code/${code}`)
    return response.data
  },

  // Create new course
  create: async (data: CreateCourseRequest): Promise<Course> => {
    const response = await api.post('/courses/', data)
    return response.data
  },

  // Update course
  update: async (id: number, data: UpdateCourseRequest): Promise<Course> => {
    const response = await api.put(`/courses/${id}`, data)
    return response.data
  },

  // Update course status (activate/deactivate)
  updateStatus: async (id: number, active: boolean): Promise<{ message: string }> => {
    const response = await api.patch(`/courses/${id}/status`, { active })
    return response.data
  },

  // Delete course (soft delete by setting active to false)
  delete: async (id: number): Promise<{ message: string }> => {
    return courseApi.updateStatus(id, false)
  },

  // Search courses
  search: async (searchRequest: CourseSearchRequest): Promise<Course[]> => {
    const response = await api.post('/courses/search', searchRequest)
    return response.data
  },
}

export const courseSessionApi = {
  // Get all sessions
  getAll: async (status?: SessionStatus, courseId?: number): Promise<CourseSession[]> => {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (courseId) params.append('course_id', courseId.toString())
    
    const response = await api.get(`/sessions/${params.toString() ? '?' + params.toString() : ''}`)
    return response.data
  },

  // Get session by ID
  getById: async (id: number): Promise<CourseSession> => {
    const response = await api.get(`/sessions/${id}`)
    return response.data
  },

  // Create new session
  create: async (data: CreateCourseSessionRequest): Promise<CourseSession> => {
    const response = await api.post('/sessions/', data)
    return response.data
  },

  // Update session
  update: async (id: number, data: UpdateCourseSessionRequest): Promise<CourseSession> => {
    const response = await api.put(`/sessions/${id}`, data)
    return response.data
  },

  // Update session status
  updateStatus: async (id: number, status: SessionStatus): Promise<{ message: string }> => {
    const response = await api.patch(`/sessions/${id}/status?status=${status}`)
    return response.data
  },

  // Search sessions
  search: async (searchRequest: SessionSearchRequest): Promise<CourseSession[]> => {
    const response = await api.post('/sessions/search', searchRequest)
    return response.data
  },

  // Get session days
  getSessionDays: async (sessionId: number) => {
    const response = await api.get(`/sessions/${sessionId}/days`)
    return response.data
  },

  // Create session day
  createSessionDay: async (sessionId: number, data: any) => {
    const response = await api.post(`/sessions/${sessionId}/days`, data)
    return response.data
  },
}

export const locationApi = {
  // Get all locations
  getAll: async (activeOnly = true): Promise<Location[]> => {
    const response = await api.get('/locations/', {
      params: { active_only: activeOnly }
    })
    return response.data
  },

  // Get location by ID
  getById: async (id: number): Promise<Location> => {
    const response = await api.get(`/locations/${id}`)
    return response.data
  },

  // Create new location
  create: async (data: CreateLocationRequest): Promise<Location> => {
    const response = await api.post('/locations/', data)
    return response.data
  },

  // Update location
  update: async (id: number, data: UpdateLocationRequest): Promise<Location> => {
    const response = await api.put(`/locations/${id}`, data)
    return response.data
  },

  // Update location status (activate/deactivate)
  updateStatus: async (id: number, active: boolean): Promise<{ message: string }> => {
    const response = await api.patch(`/locations/${id}/status?active=${active}`)
    return response.data
  },

  // Delete location (soft delete by setting active to false)
  delete: async (id: number): Promise<{ message: string }> => {
    return locationApi.updateStatus(id, false)
  },

  // Search locations
  search: async (searchRequest: LocationSearchRequest): Promise<Location[]> => {
    const response = await api.post('/locations/search', searchRequest)
    return response.data
  },
}

export default api