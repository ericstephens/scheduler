import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import type { CourseSession } from '@/types/courseSession'
import { SessionStatus } from '@/types/courseSession'
import { 
  useCourseSessions, 
  useCreateCourseSession, 
  useUpdateCourseSession,
  useUpdateCourseSessionStatus 
} from '@/hooks/useCourseSessions'
import { useCourses } from '@/hooks/useCourses'
import CourseSessionList from '@/components/sessions/CourseSessionList'
import CourseSessionForm from '@/components/sessions/CourseSessionForm'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'

type ModalState = 'create' | 'edit' | 'delete' | null

export default function Sessions() {
  const [modalState, setModalState] = useState<ModalState>(null)
  const [selectedSession, setSelectedSession] = useState<CourseSession | null>(null)

  const { data: courseSessions = [], isLoading } = useCourseSessions()
  const { data: courses = [] } = useCourses()
  const createMutation = useCreateCourseSession()
  const updateMutation = useUpdateCourseSession()
  const updateStatusMutation = useUpdateCourseSessionStatus()

  const handleCreateNew = () => {
    setSelectedSession(null)
    setModalState('create')
  }

  const handleEdit = (courseSession: CourseSession) => {
    setSelectedSession(courseSession)
    setModalState('edit')
  }

  const handleDelete = (courseSession: CourseSession) => {
    setSelectedSession(courseSession)
    setModalState('delete')
  }

  const handleUpdateStatus = (courseSession: CourseSession, status: SessionStatus) => {
    updateStatusMutation.mutate({
      id: courseSession.id,
      status
    })
  }

  const handleSubmitForm = async (data: any) => {
    if (selectedSession) {
      await updateMutation.mutateAsync({
        id: selectedSession.id,
        data
      })
    } else {
      await createMutation.mutateAsync(data)
    }
    setModalState(null)
    setSelectedSession(null)
  }

  const handleConfirmDelete = () => {
    if (selectedSession) {
      // For now, we'll just set status to cancelled since there's no delete endpoint
      updateStatusMutation.mutate({
        id: selectedSession.id,
        status: SessionStatus.CANCELLED
      })
      setModalState(null)
      setSelectedSession(null)
    }
  }

  const handleCloseModal = () => {
    setModalState(null)
    setSelectedSession(null)
  }

  const isFormLoading = createMutation.isLoading || updateMutation.isLoading

  return (
    <div className="p-8">
      <CourseSessionList
        courseSessions={courseSessions}
        courses={courses}
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
        title={selectedSession ? 'Edit Course Session' : 'Add New Course Session'}
        size="lg"
      >
        <CourseSessionForm
          courseSession={selectedSession || undefined}
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
        {selectedSession && (
          <div className="space-y-4">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Delete Session
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to delete{' '}
                <strong>
                  {selectedSession.session_name}
                </strong>
                ? This action will cancel the session and cannot be undone.
              </p>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
              <Button
                variant="outline"
                onClick={handleCloseModal}
                disabled={updateStatusMutation.isLoading}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleConfirmDelete}
                disabled={updateStatusMutation.isLoading}
                className="min-w-[100px]"
              >
                {updateStatusMutation.isLoading ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}