import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import type { Location } from '@/types/location'
import { 
  useLocations, 
  useCreateLocation, 
  useUpdateLocation,
  useDeleteLocation,
  useUpdateLocationStatus
} from '@/hooks/useLocations'
import LocationList from '@/components/locations/LocationList'
import LocationForm from '@/components/locations/LocationForm'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'

type ModalState = 'create' | 'edit' | 'delete' | null

export default function Locations() {
  const [modalState, setModalState] = useState<ModalState>(null)
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null)

  const { data: locations = [], isLoading } = useLocations()
  const createMutation = useCreateLocation()
  const updateMutation = useUpdateLocation()
  const deleteMutation = useDeleteLocation()
  const updateStatusMutation = useUpdateLocationStatus()

  const handleCreateNew = () => {
    setSelectedLocation(null)
    setModalState('create')
  }

  const handleEdit = (location: Location) => {
    setSelectedLocation(location)
    setModalState('edit')
  }

  const handleDelete = (location: Location) => {
    setSelectedLocation(location)
    setModalState('delete')
  }

  const handleUpdateStatus = (location: Location, active: boolean) => {
    updateStatusMutation.mutate({
      id: location.id,
      active
    })
  }

  const handleSubmitForm = async (data: any) => {
    if (selectedLocation) {
      await updateMutation.mutateAsync({
        id: selectedLocation.id,
        data
      })
    } else {
      await createMutation.mutateAsync(data)
    }
    setModalState(null)
    setSelectedLocation(null)
  }

  const handleConfirmDelete = () => {
    if (selectedLocation) {
      deleteMutation.mutate(selectedLocation.id)
      setModalState(null)
      setSelectedLocation(null)
    }
  }

  const handleCloseModal = () => {
    setModalState(null)
    setSelectedLocation(null)
  }

  const isFormLoading = createMutation.isLoading || updateMutation.isLoading

  return (
    <div className="p-8">
      <LocationList
        locations={locations}
        onCreateNew={handleCreateNew}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onUpdateStatus={handleUpdateStatus}
        isLoading={isLoading}
      />

      {/* Create/Edit Modal */}
      <Modal
        isOpen={modalState === 'create' || modalState === 'edit'}
        onClose={handleCloseModal}
        title={selectedLocation ? 'Edit Location' : 'Add New Location'}
        size="lg"
      >
        <LocationForm
          location={selectedLocation || undefined}
          onSubmit={handleSubmitForm}
          onCancel={handleCloseModal}
          isLoading={isFormLoading}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={modalState === 'delete'}
        onClose={handleCloseModal}
        title="Confirm Deletion"
        size="sm"
      >
        {selectedLocation && (
          <div className="space-y-4">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Delete Location
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to delete{' '}
                <strong>
                  {selectedLocation.location_name}
                </strong>
                ? This action will deactivate the location and cannot be undone.
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <Button
                variant="outline"
                onClick={handleCloseModal}
                disabled={deleteMutation.isLoading}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleConfirmDelete}
                disabled={deleteMutation.isLoading}
                className="min-w-[100px]"
              >
                {deleteMutation.isLoading ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}