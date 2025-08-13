import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Instructor, CreateInstructorRequest } from '@/types/instructor'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const instructorSchema = z.object({
  first_name: z.string().min(1, 'First name is required').max(100, 'First name must be less than 100 characters'),
  last_name: z.string().min(1, 'Last name is required').max(100, 'Last name must be less than 100 characters'),
  email: z.string().email('Invalid email address').max(255, 'Email must be less than 255 characters'),
  phone_number: z.string().optional(),
  call_sign: z.string().max(50, 'Call sign must be less than 50 characters').optional(),
  notes: z.string().optional(),
})

type InstructorFormData = z.infer<typeof instructorSchema>

interface InstructorFormProps {
  instructor?: Instructor
  onSubmit: (data: CreateInstructorRequest) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function InstructorForm({ 
  instructor, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}: InstructorFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<InstructorFormData>({
    resolver: zodResolver(instructorSchema),
    mode: 'onChange',
    defaultValues: {
      first_name: instructor?.first_name || '',
      last_name: instructor?.last_name || '',
      email: instructor?.email || '',
      phone_number: instructor?.phone_number || '',
      call_sign: instructor?.call_sign || '',
      notes: instructor?.notes || '',
    },
  })

  useEffect(() => {
    if (instructor) {
      reset({
        first_name: instructor.first_name,
        last_name: instructor.last_name,
        email: instructor.email,
        phone_number: instructor.phone_number || '',
        call_sign: instructor.call_sign || '',
        notes: instructor.notes || '',
      })
    }
  }, [instructor, reset])

  const handleFormSubmit = async (data: InstructorFormData) => {
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
          label="First Name"
          {...register('first_name')}
          error={errors.first_name?.message}
          placeholder="John"
          required
        />
        
        <Input
          label="Last Name"
          {...register('last_name')}
          error={errors.last_name?.message}
          placeholder="Doe"
          required
        />
      </div>

      <Input
        label="Email"
        type="email"
        {...register('email')}
        error={errors.email?.message}
        placeholder="john.doe@example.com"
        required
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Phone Number"
          type="tel"
          {...register('phone_number')}
          error={errors.phone_number?.message}
          placeholder="(555) 123-4567"
        />
        
        <Input
          label="Call Sign"
          {...register('call_sign')}
          error={errors.call_sign?.message}
          placeholder="Alpha-1"
        />
      </div>

      <div>
        <label className="text-sm font-medium text-gray-700">Notes</label>
        <textarea
          {...register('notes')}
          rows={3}
          className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Additional notes about the instructor..."
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
          disabled={!isValid || isLoading}
          className="min-w-[120px]"
        >
          {isLoading ? (
            <div className="flex items-center">
              <LoadingSpinner size="sm" className="mr-2" />
              {instructor ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            instructor ? 'Update Instructor' : 'Create Instructor'
          )}
        </Button>
      </div>
    </form>
  )
}