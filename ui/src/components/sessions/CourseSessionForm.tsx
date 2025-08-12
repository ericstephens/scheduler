import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { CourseSession, CreateCourseSessionRequest } from '@/types/courseSession'
import { useCourses } from '@/hooks/useCourses'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const courseSessionSchema = z.object({
  course_id: z.number().min(1, 'Course is required'),
  session_name: z.string().min(1, 'Session name is required').max(200, 'Session name must be less than 200 characters'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  notes: z.string().optional(),
}).refine((data) => {
  const startDate = new Date(data.start_date)
  const endDate = new Date(data.end_date)
  return endDate >= startDate
}, {
  message: "End date must be on or after start date",
  path: ["end_date"],
})

type CourseSessionFormData = z.infer<typeof courseSessionSchema>

interface CourseSessionFormProps {
  courseSession?: CourseSession
  onSubmit: (data: CreateCourseSessionRequest) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function CourseSessionForm({ 
  courseSession, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}: CourseSessionFormProps) {
  const { data: courses = [], isLoading: coursesLoading } = useCourses()
  
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<CourseSessionFormData>({
    resolver: zodResolver(courseSessionSchema),
    mode: 'onChange',
    defaultValues: {
      course_id: courseSession?.course_id || 0,
      session_name: courseSession?.session_name || '',
      start_date: courseSession?.start_date || '',
      end_date: courseSession?.end_date || '',
      notes: courseSession?.notes || '',
    },
  })

  useEffect(() => {
    if (courseSession) {
      reset({
        course_id: courseSession.course_id,
        session_name: courseSession.session_name,
        start_date: courseSession.start_date,
        end_date: courseSession.end_date,
        notes: courseSession.notes || '',
      })
    }
  }, [courseSession, reset])

  const handleFormSubmit = async (data: CourseSessionFormData) => {
    try {
      await onSubmit(data)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Course Picker */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Course <span className="text-red-500">*</span>
        </label>
        <Controller
          name="course_id"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              value={field.value || ''}
              onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
              className="block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={coursesLoading}
            >
              <option value="">
                {coursesLoading ? 'Loading courses...' : 'Select a course'}
              </option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.course_code} - {course.course_name}
                </option>
              ))}
            </select>
          )}
        />
        {errors.course_id && (
          <p className="mt-1 text-sm text-red-600">{errors.course_id.message}</p>
        )}
      </div>

      <Input
        label="Session Name"
        {...register('session_name')}
        error={errors.session_name?.message}
        placeholder="Introduction to JavaScript - Spring 2024"
        required
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Start Date"
          type="date"
          {...register('start_date')}
          error={errors.start_date?.message}
          required
        />
        
        <Input
          label="End Date"
          type="date"
          {...register('end_date')}
          error={errors.end_date?.message}
          required
        />
      </div>

      <div>
        <label className="text-sm font-medium text-gray-700">Notes</label>
        <textarea
          {...register('notes')}
          rows={4}
          className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Additional notes about the session..."
        />
        {errors.notes && (
          <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
        )}
      </div>

      <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        
        <Button
          type="submit"
          disabled={!isValid || isLoading || coursesLoading}
          className="min-w-[120px]"
        >
          {isLoading ? (
            <div className="flex items-center">
              <LoadingSpinner size="sm" className="mr-2" />
              {courseSession ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            courseSession ? 'Update Session' : 'Create Session'
          )}
        </Button>
      </div>
    </form>
  )
}