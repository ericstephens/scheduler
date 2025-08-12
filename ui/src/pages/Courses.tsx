import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import type { Course } from '@/types/course'
import { 
  useCourses, 
  useCreateCourse, 
  useUpdateCourse, 
  useDeleteCourse,
  useUpdateCourseStatus 
} from '@/hooks/useCourses'
import CourseList from '@/components/courses/CourseList'
import CourseForm from '@/components/courses/CourseForm'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'

type ModalState = 'create' | 'edit' | 'delete' | null

export default function Courses() {
  const [modalState, setModalState] = useState<ModalState>(null)
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null)
  const [showInactive, setShowInactive] = useState(false)

  const { data: courses = [], isLoading } = useCourses(!showInactive)
  const createMutation = useCreateCourse()
  const updateMutation = useUpdateCourse()
  const deleteMutation = useDeleteCourse()
  const updateStatusMutation = useUpdateCourseStatus()

  const handleCreateNew = () => {
    setSelectedCourse(null)
    setModalState('create')
  }

  const handleEdit = (course: Course) => {
    setSelectedCourse(course)
    setModalState('edit')
  }

  const handleDelete = (course: Course) => {
    setSelectedCourse(course)
    setModalState('delete')
  }

  const handleToggleStatus = (course: Course) => {
    updateStatusMutation.mutate({
      id: course.id,
      active: !course.active_status
    })
  }

  const handleSubmitForm = async (data: any) => {
    if (selectedCourse) {
      await updateMutation.mutateAsync({
        id: selectedCourse.id,
        data
      })
    } else {
      await createMutation.mutateAsync(data)
    }
    setModalState(null)
    setSelectedCourse(null)
  }

  const handleConfirmDelete = () => {
    if (selectedCourse) {
      deleteMutation.mutate(selectedCourse.id)
      setModalState(null)
      setSelectedCourse(null)
    }
  }

  const handleCloseModal = () => {
    setModalState(null)
    setSelectedCourse(null)
  }

  const isFormLoading = createMutation.isLoading || updateMutation.isLoading

  return (
    <div className="p-8">
      <CourseList
        courses={courses}
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
        title={selectedCourse ? 'Edit Course' : 'Add New Course'}
        size="lg"
      >
        <CourseForm
          course={selectedCourse || undefined}
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
        {selectedCourse && (
          <div className="space-y-4">
            <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Delete Course
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to delete{' '}
                <strong>
                  {selectedCourse.course_name} ({selectedCourse.course_code})
                </strong>
                ? This action cannot be undone and will deactivate the course.
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