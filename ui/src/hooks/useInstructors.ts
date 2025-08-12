import { useMutation, useQuery, useQueryClient } from 'react-query'
import { instructorApi } from '@/services/api'
import type { Instructor, CreateInstructorRequest, UpdateInstructorRequest } from '@/types/instructor'
import toast from 'react-hot-toast'

export const useInstructors = (activeOnly = true) => {
  return useQuery(
    ['instructors', { activeOnly }],
    () => instructorApi.getAll(activeOnly),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

export const useInstructor = (id: number) => {
  return useQuery(
    ['instructor', id],
    () => instructorApi.getById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCreateInstructor = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (data: CreateInstructorRequest) => instructorApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['instructors'])
        toast.success('Instructor created successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create instructor')
      },
    }
  )
}

export const useUpdateInstructor = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, data }: { id: number; data: UpdateInstructorRequest }) =>
      instructorApi.update(id, data),
    {
      onSuccess: (updatedInstructor) => {
        queryClient.invalidateQueries(['instructors'])
        queryClient.invalidateQueries(['instructor', updatedInstructor.id])
        toast.success('Instructor updated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update instructor')
      },
    }
  )
}

export const useDeleteInstructor = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (id: number) => instructorApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['instructors'])
        toast.success('Instructor deactivated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to deactivate instructor')
      },
    }
  )
}

export const useUpdateInstructorStatus = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, active }: { id: number; active: boolean }) =>
      instructorApi.updateStatus(id, active),
    {
      onSuccess: (_, { active }) => {
        queryClient.invalidateQueries(['instructors'])
        toast.success(`Instructor ${active ? 'activated' : 'deactivated'} successfully`)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update instructor status')
      },
    }
  )
}

export const useInstructorStats = (id: number) => {
  return useQuery(
    ['instructor-stats', id],
    () => instructorApi.getStats(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  )
}