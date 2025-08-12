import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Course, CreateCourseRequest } from '@/types/course'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const courseSchema = z.object({
  course_name: z.string().min(1, 'Course name is required').max(200, 'Course name must be less than 200 characters'),
  course_code: z.string().min(1, 'Course code is required').max(50, 'Course code must be less than 50 characters'),
  description: z.string().optional(),
  duration_days: z.number().min(1, 'Duration must be at least 1 day').max(365, 'Duration must be less than 365 days'),
})

type CourseFormData = z.infer<typeof courseSchema>

interface CourseFormProps {
  course?: Course
  onSubmit: (data: CreateCourseRequest) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function CourseForm({ 
  course, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}: CourseFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<CourseFormData>({
    resolver: zodResolver(courseSchema),
    mode: 'onChange',
    defaultValues: {
      course_name: course?.course_name || '',
      course_code: course?.course_code || '',
      description: course?.description || '',
      duration_days: course?.duration_days || 1,
    },
  })

  useEffect(() => {
    if (course) {
      reset({
        course_name: course.course_name,
        course_code: course.course_code,
        description: course.description || '',
        duration_days: course.duration_days,
      })
    }
  }, [course, reset])

  const handleFormSubmit = async (data: CourseFormData) => {
    try {
      await onSubmit(data)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Course Name"
          {...register('course_name')}
          error={errors.course_name?.message}
          placeholder="Advanced JavaScript"
          required
        />
        
        <Input
          label="Course Code"
          {...register('course_code')}
          error={errors.course_code?.message}
          placeholder="ADV-JS-101"
          required
        />
      </div>

      <Input
        label="Duration (Days)"
        type="number"
        {...register('duration_days', { valueAsNumber: true })}
        error={errors.duration_days?.message}
        placeholder="5"
        required
        min="1"
        max="365"
      />

      <div>
        <label className="text-sm font-medium text-gray-700">Description</label>
        <textarea
          {...register('description')}
          rows={4}
          className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Course description and learning objectives..."
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
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
          disabled={!isValid || isLoading}
          className="min-w-[120px]"
        >
          {isLoading ? (
            <div className="flex items-center">
              <LoadingSpinner size="sm" className="mr-2" />
              {course ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            course ? 'Update Course' : 'Create Course'
          )}
        </Button>
      </div>
    </form>
  )
}