import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Location, CreateLocationRequest } from '@/types/location'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

const locationSchema = z.object({
  location_name: z.string().min(1, 'Location name is required').max(200, 'Location name must be less than 200 characters'),
  address: z.string().max(255, 'Address must be less than 255 characters').optional(),
  city: z.string().max(100, 'City must be less than 100 characters').optional(),
  state_province: z.string().max(50, 'State/Province must be less than 50 characters').optional(),
  postal_code: z.string().max(20, 'Postal code must be less than 20 characters').optional(),
  notes: z.string().optional(),
})

type LocationFormData = z.infer<typeof locationSchema>

interface LocationFormProps {
  location?: Location
  onSubmit: (data: CreateLocationRequest) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function LocationForm({ 
  location, 
  onSubmit, 
  onCancel, 
  isLoading = false 
}: LocationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
  } = useForm<LocationFormData>({
    resolver: zodResolver(locationSchema),
    mode: 'onChange',
    defaultValues: {
      location_name: location?.location_name || '',
      address: location?.address || '',
      city: location?.city || '',
      state_province: location?.state_province || '',
      postal_code: location?.postal_code || '',
      notes: location?.notes || '',
    },
  })

  useEffect(() => {
    if (location) {
      reset({
        location_name: location.location_name,
        address: location.address || '',
        city: location.city || '',
        state_province: location.state_province || '',
        postal_code: location.postal_code || '',
        notes: location.notes || '',
      })
    }
  }, [location, reset])

  const handleFormSubmit = async (data: LocationFormData) => {
    try {
      await onSubmit(data)
    } catch (error) {
      console.error('Form submission error:', error)
    }
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <Input
        label="Location Name"
        {...register('location_name')}
        error={errors.location_name?.message}
        placeholder="Main Training Center"
        required
      />

      <Input
        label="Address"
        {...register('address')}
        error={errors.address?.message}
        placeholder="123 Main Street"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="City"
          {...register('city')}
          error={errors.city?.message}
          placeholder="Springfield"
        />
        
        <Input
          label="State/Province"
          {...register('state_province')}
          error={errors.state_province?.message}
          placeholder="IL"
        />
      </div>

      <Input
        label="Postal Code"
        {...register('postal_code')}
        error={errors.postal_code?.message}
        placeholder="62701"
      />

      <div>
        <label className="text-sm font-medium text-gray-700">Notes</label>
        <textarea
          {...register('notes')}
          rows={3}
          className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Additional notes about the location..."
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
              {location ? 'Updating...' : 'Creating...'}
            </div>
          ) : (
            location ? 'Update Location' : 'Create Location'
          )}
        </Button>
      </div>
    </form>
  )
}