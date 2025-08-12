export interface Course {
  id: number
  course_name: string
  course_code: string
  description?: string
  duration_days: number
  active_status: boolean
  created_date: string
}

export interface CreateCourseRequest {
  course_name: string
  course_code: string
  description?: string
  duration_days: number
}

export interface UpdateCourseRequest {
  course_name?: string
  course_code?: string
  description?: string
  duration_days?: number
}

export interface CourseSearchRequest {
  name?: string
  code?: string
  active_only: boolean
}