import { useMutation, useQuery, useQueryClient } from 'react-query'
import { courseApi } from '@/services/api'
import type { CreateCourseRequest, UpdateCourseRequest } from '@/types/course'
import toast from 'react-hot-toast'

export const useCourses = (activeOnly = true) => {
  return useQuery(
    ['courses', { activeOnly }],
    () => courseApi.getAll(activeOnly),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

export const useCourse = (id: number) => {
  return useQuery(
    ['course', id],
    () => courseApi.getById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCourseByCode = (code: string) => {
  return useQuery(
    ['course-by-code', code],
    () => courseApi.getByCode(code),
    {
      enabled: !!code,
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCreateCourse = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (data: CreateCourseRequest) => courseApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['courses'])
        toast.success('Course created successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create course')
      },
    }
  )
}

export const useUpdateCourse = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, data }: { id: number; data: UpdateCourseRequest }) =>
      courseApi.update(id, data),
    {
      onSuccess: (updatedCourse) => {
        queryClient.invalidateQueries(['courses'])
        queryClient.invalidateQueries(['course', updatedCourse.id])
        queryClient.invalidateQueries(['course-by-code', updatedCourse.course_code])
        toast.success('Course updated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update course')
      },
    }
  )
}

export const useDeleteCourse = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (id: number) => courseApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['courses'])
        toast.success('Course deactivated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to deactivate course')
      },
    }
  )
}

export const useUpdateCourseStatus = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, active }: { id: number; active: boolean }) =>
      courseApi.updateStatus(id, active),
    {
      onSuccess: (_, { active }) => {
        queryClient.invalidateQueries(['courses'])
        toast.success(`Course ${active ? 'activated' : 'deactivated'} successfully`)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update course status')
      },
    }
  )
}