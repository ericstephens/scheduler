import { useMutation, useQuery, useQueryClient } from 'react-query'
import { locationApi } from '@/services/api'
import type { CreateLocationRequest, UpdateLocationRequest } from '@/types/location'
import toast from 'react-hot-toast'

export const useLocations = (activeOnly = true) => {
  return useQuery(
    ['locations', { activeOnly }],
    () => locationApi.getAll(activeOnly),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )
}

export const useLocation = (id: number) => {
  return useQuery(
    ['location', id],
    () => locationApi.getById(id),
    {
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCreateLocation = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (data: CreateLocationRequest) => locationApi.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['locations'])
        toast.success('Location created successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create location')
      },
    }
  )
}

export const useUpdateLocation = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, data }: { id: number; data: UpdateLocationRequest }) =>
      locationApi.update(id, data),
    {
      onSuccess: (updatedLocation) => {
        queryClient.invalidateQueries(['locations'])
        queryClient.invalidateQueries(['location', updatedLocation.id])
        toast.success('Location updated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update location')
      },
    }
  )
}

export const useDeleteLocation = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (id: number) => locationApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['locations'])
        toast.success('Location deactivated successfully')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to deactivate location')
      },
    }
  )
}

export const useUpdateLocationStatus = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ id, active }: { id: number; active: boolean }) =>
      locationApi.updateStatus(id, active),
    {
      onSuccess: (_, { active }) => {
        queryClient.invalidateQueries(['locations'])
        toast.success(`Location ${active ? 'activated' : 'deactivated'} successfully`)
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update location status')
      },
    }
  )
}