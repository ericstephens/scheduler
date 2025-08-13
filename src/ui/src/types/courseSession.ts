export enum SessionStatus {
  SCHEDULED = "scheduled",
  IN_PROGRESS = "in_progress", 
  COMPLETED = "completed",
  CANCELLED = "cancelled"
}

export enum SessionType {
  HALF_DAY = "half_day",
  FULL_DAY = "full_day"
}

export interface CourseSession {
  id: number
  course_id: number
  session_name: string
  start_date: string
  end_date: string
  status: SessionStatus
  notes?: string
}

export interface CreateCourseSessionRequest {
  course_id: number
  session_name: string
  start_date: string
  end_date: string
  notes?: string
}

export interface UpdateCourseSessionRequest {
  session_name?: string
  start_date?: string
  end_date?: string
  status?: SessionStatus
  notes?: string
}

export interface CourseSessionDay {
  id: number
  session_id: number
  day_number: number
  date: string
  location_id: number
  start_time: string
  end_time: string
  session_type: SessionType
}

export interface CreateCourseSessionDayRequest {
  session_id: number
  day_number: number
  date: string
  location_id: number
  start_time: string
  end_time: string
  session_type: SessionType
}

export interface UpdateCourseSessionDayRequest {
  day_number?: number
  date?: string
  location_id?: number
  start_time?: string
  end_time?: string
  session_type?: SessionType
}

export interface SessionSearchRequest {
  course_id?: number
  status?: SessionStatus
  start_date_from?: string
  start_date_to?: string
  location_id?: number
}