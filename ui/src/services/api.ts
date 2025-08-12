import axios from 'axios'
import type { Instructor, CreateInstructorRequest, UpdateInstructorRequest, InstructorStats } from '@/types/instructor'
import type { Course, CreateCourseRequest, UpdateCourseRequest, CourseSearchRequest } from '@/types/course'

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

export default api