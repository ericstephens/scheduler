import { useMutation, useQuery, useQueryClient } from 'react-query'
import { courseSessionApi } from '@/services/api'
import type { CreateCourseSessionRequest, UpdateCourseSessionRequest, SessionStatus } from '@/types/courseSession'
import toast from 'react-hot-toast'

export const useCourseSessions = (status?: SessionStatus, courseId?: number) => {
  return useQuery(
    ['course-sessions', { status, courseId }],
    () => courseSessionApi.getAll(status, courseId),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

export const useCourseSession = (id: number) => {
  return useQuery(
    ['course-session', id],
    () => courseSessionApi.getById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCreateCourseSession = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (data: CreateCourseSessionRequest) => courseSessionApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['course-sessions'])
        toast.success('Course session created successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create course session')
      },
    }
  )
}

export const useUpdateCourseSession = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, data }: { id: number; data: UpdateCourseSessionRequest }) =>
      courseSessionApi.update(id, data),
    {
      onSuccess: (updatedSession) => {
        queryClient.invalidateQueries(['course-sessions'])
        queryClient.invalidateQueries(['course-session', updatedSession.id])
        toast.success('Course session updated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update course session')
      },
    }
  )
}

export const useUpdateCourseSessionStatus = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, status }: { id: number; status: SessionStatus }) =>
      courseSessionApi.updateStatus(id, status),
    {
      onSuccess: (_, { status }) => {
        queryClient.invalidateQueries(['course-sessions'])
        toast.success(`Session status updated to ${status}`)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update session status')
      },
    }
  )
}

export const useSessionDays = (sessionId: number) => {
  return useQuery(
    ['session-days', sessionId],
    () => courseSessionApi.getSessionDays(sessionId),
    {
      enabled: !!sessionId,
      staleTime: 5 * 60 * 1000,
    }
  )
}