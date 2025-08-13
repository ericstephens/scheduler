import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { 
  CourseSessionDay, 
  CreateCourseSessionDayRequest, 
  UpdateCourseSessionDayRequest 
} from '@/types/courseSession'
import { SessionType } from '@/types/courseSession'
import type { Location } from '@/types/location'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

const sessionDaySchema = z.object({
  day_number: z.number().min(1, 'Day number must be at least 1'),
  date: z.string().min(1, 'Date is required'),
  location_id: z.number().min(1, 'Location is required'),
  start_time: z.string().min(1, 'Start time is required'),
  end_time: z.string().min(1, 'End time is required'),
  session_type: z.nativeEnum(SessionType)
}).refine((data) => {
  if (data.start_time && data.end_time) {
    return data.start_time < data.end_time
  }
  return true
}, {
  message: 'End time must be after start time',
  path: ['end_time']
})

type SessionDayFormData = z.infer<typeof sessionDaySchema>

interface SessionDayFormProps {
  sessionDay?: CourseSessionDay
  sessionId: number
  locations: Location[]
  onSubmit: (data: CreateCourseSessionDayRequest | UpdateCourseSessionDayRequest) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

export default function SessionDayForm({ 
  sessionDay, 
  sessionId,
  locations,
  onSubmit, 
  onCancel, 
  loading = false 
}: SessionDayFormProps) {
  const isEditing = !!sessionDay

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setValue,
    watch
  } = useForm<SessionDayFormData>({
    resolver: zodResolver(sessionDaySchema),
    defaultValues: sessionDay ? {
      day_number: sessionDay.day_number,
      date: sessionDay.date,
      location_id: sessionDay.location_id,
      start_time: sessionDay.start_time,
      end_time: sessionDay.end_time,
      session_type: sessionDay.session_type
    } : {
      day_number: 1,
      date: '',
      location_id: 0,
      start_time: '09:00',
      end_time: '17:00',
      session_type: SessionType.FULL_DAY
    }
  })

  const sessionType = watch('session_type')

  // Update end time based on session type
  useEffect(() => {
    const startTime = watch('start_time')
    if (sessionType === SessionType.HALF_DAY && startTime) {
      const [hours, minutes] = startTime.split(':')
      const startHour = parseInt(hours, 10)
      const endHour = startHour + 4 // 4 hours for half day
      setValue('end_time', `${endHour.toString().padStart(2, '0')}:${minutes}`)
    }
  }, [sessionType, watch('start_time'), setValue])

  const onFormSubmit = async (data: SessionDayFormData) => {
    try {
      if (isEditing) {
        const updateData: UpdateCourseSessionDayRequest = {
          day_number: data.day_number,
          date: data.date,
          location_id: data.location_id,
          start_time: data.start_time,
          end_time: data.end_time,
          session_type: data.session_type
        }
        await onSubmit(updateData)
      } else {
        const createData: CreateCourseSessionDayRequest = {
          session_id: sessionId,
          day_number: data.day_number,
          date: data.date,
          location_id: data.location_id,
          start_time: data.start_time,
          end_time: data.end_time,
          session_type: data.session_type
        }
        await onSubmit(createData)
      }
    } catch (error) {
      // Error handling is done in parent component
    }
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="day_number" className="block text-sm font-medium text-gray-700 mb-2">
            Day Number
          </label>
          <Input
            id="day_number"
            type="number"
            min="1"
            {...register('day_number', { valueAsNumber: true })}
            error={errors.day_number?.message}
            disabled={loading || isSubmitting}
          />
        </div>

        <div>
          <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
            Date
          </label>
          <Input
            id="date"
            type="date"
            {...register('date')}
            error={errors.date?.message}
            disabled={loading || isSubmitting}
          />
        </div>

        <div>
          <label htmlFor="location_id" className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <select
            id="location_id"
            {...register('location_id', { valueAsNumber: true })}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            disabled={loading || isSubmitting}
          >
            <option value={0}>Select a location</option>
            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.location_name}
              </option>
            ))}
          </select>
          {errors.location_id && (
            <p className="mt-1 text-sm text-red-600">{errors.location_id.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="session_type" className="block text-sm font-medium text-gray-700 mb-2">
            Session Type
          </label>
          <select
            id="session_type"
            {...register('session_type')}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            disabled={loading || isSubmitting}
          >
            <option value={SessionType.HALF_DAY}>Half Day</option>
            <option value={SessionType.FULL_DAY}>Full Day</option>
          </select>
          {errors.session_type && (
            <p className="mt-1 text-sm text-red-600">{errors.session_type.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="start_time" className="block text-sm font-medium text-gray-700 mb-2">
            Start Time
          </label>
          <Input
            id="start_time"
            type="time"
            {...register('start_time')}
            error={errors.start_time?.message}
            disabled={loading || isSubmitting}
          />
        </div>

        <div>
          <label htmlFor="end_time" className="block text-sm font-medium text-gray-700 mb-2">
            End Time
          </label>
          <Input
            id="end_time"
            type="time"
            {...register('end_time')}
            error={errors.end_time?.message}
            disabled={loading || isSubmitting}
          />
        </div>
      </div>

      <div className="flex justify-end space-x-3">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading || isSubmitting}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          loading={loading || isSubmitting}
        >
          {isEditing ? 'Update Session Day' : 'Create Session Day'}
        </Button>
      </div>
    </form>
  )
}