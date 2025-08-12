export interface Instructor {
  id: number
  first_name: string
  last_name: string
  email: string
  phone_number?: string
  call_sign?: string
  active_status: boolean
  created_date: string
  notes?: string
}

export interface CreateInstructorRequest {
  first_name: string
  last_name: string
  email: string
  phone_number?: string
  call_sign?: string
  notes?: string
}

export interface UpdateInstructorRequest {
  first_name?: string
  last_name?: string
  email?: string
  phone_number?: string
  call_sign?: string
  notes?: string
}

export interface InstructorStats {
  total_assignments: number
  total_course_ratings: number
  cleared_courses: number
}