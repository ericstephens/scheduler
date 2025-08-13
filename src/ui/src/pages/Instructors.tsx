import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import type { Instructor } from '@/types/instructor'
import { 
  useInstructors, 
  useCreateInstructor, 
  useUpdateInstructor, 
  useDeleteInstructor,
  useUpdateInstructorStatus 
} from '@/hooks/useInstructors'
import InstructorList from '@/components/instructors/InstructorList'
import InstructorForm from '@/components/instructors/InstructorForm'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'

type ModalState = 'create' | 'edit' | 'delete' | null

export default function Instructors() {
  const [modalState, setModalState] = useState<ModalState>(null)
  const [selectedInstructor, setSelectedInstructor] = useState<Instructor | null>(null)
  const [showInactive, setShowInactive] = useState(false)

  const { data: instructors = [], isLoading } = useInstructors(!showInactive)
  const createMutation = useCreateInstructor()
  const updateMutation = useUpdateInstructor()
  const deleteMutation = useDeleteInstructor()
  const updateStatusMutation = useUpdateInstructorStatus()

  const handleCreateNew = () => {
    setSelectedInstructor(null)
    setModalState('create')
  }

  const handleEdit = (instructor: Instructor) => {
    setSelectedInstructor(instructor)
    setModalState('edit')
  }

  const handleDelete = (instructor: Instructor) => {
    setSelectedInstructor(instructor)
    setModalState('delete')
  }

  const handleToggleStatus = (instructor: Instructor) => {
    updateStatusMutation.mutate({
      id: instructor.id,
      active: !instructor.active_status
    })
  }

  const handleSubmitForm = async (data: any) => {
    if (selectedInstructor) {
      await updateMutation.mutateAsync({
        id: selectedInstructor.id,
        data
      })
    } else {
      await createMutation.mutateAsync(data)
    }
    setModalState(null)
    setSelectedInstructor(null)
  }

  const handleConfirmDelete = () => {
    if (selectedInstructor) {
      deleteMutation.mutate(selectedInstructor.id)
      setModalState(null)
      setSelectedInstructor(null)
    }
  }

  const handleCloseModal = () => {
    setModalState(null)
    setSelectedInstructor(null)
  }

  const isFormLoading = createMutation.isLoading || updateMutation.isLoading

  return (
    <div className="p-8">
      <InstructorList
        instructors={instructors}
        onCreateNew={handleCreateNew}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onToggleStatus={handleToggleStatus}
        isLoading={isLoading}
        showInactive={!showInactive}
        onToggleInactive={setShowInactive}
      />

      {/* Create/Edit Modal */}
      <Modal
        isOpen={modalState === 'create' || modalState === 'edit'}
        onClose={handleCloseModal}
        title={selectedInstructor ? 'Edit Instructor' : 'Add New Instructor'}
        size="lg"
      >
        <InstructorForm
          instructor={selectedInstructor || undefined}
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
        {selectedInstructor && (
          <div className="space-y-4">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Delete Instructor
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to delete{' '}
                <strong>
                  {selectedInstructor.first_name} {selectedInstructor.last_name}
                </strong>
                ? This action cannot be undone and will deactivate the instructor.
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