import { useState } from 'react'
import { Plus, Calendar, Filter } from 'lucide-react'
import { useSessionDaysBySession } from '@/hooks/useSessionDays'
import { useLocations } from '@/hooks/useLocations'
import SessionDayCard from './SessionDayCard'
import SessionDayForm from './SessionDayForm'
import type { CourseSessionDay, CreateCourseSessionDayRequest, UpdateCourseSessionDayRequest } from '@/types/courseSession'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import Modal from '@/components/ui/Modal'
import ErrorBoundary from '@/components/ErrorBoundary'

interface SessionDayListProps {
  sessionId: number
  sessionName?: string
  courseName?: string
}

export default function SessionDayList({ sessionId, sessionName, courseName }: SessionDayListProps) {
  const [showForm, setShowForm] = useState(false)
  const [editingSessionDay, setEditingSessionDay] = useState<CourseSessionDay | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<CourseSessionDay | null>(null)
  const [formLoading, setFormLoading] = useState(false)

  const {
    sessionDays,
    loading,
    error,
    refetch,
    createSessionDay,
    updateSessionDay,
    deleteSessionDay
  } = useSessionDaysBySession(sessionId)

  const { data: locations = [] } = useLocations()

  const handleCreateSessionDay = async (data: CreateCourseSessionDayRequest) => {
    try {
      setFormLoading(true)
      await createSessionDay(data)
      setShowForm(false)
    } catch (error) {
      console.error('Failed to create session day:', error)
      throw error
    } finally {
      setFormLoading(false)
    }
  }

  const handleUpdateSessionDay = async (data: UpdateCourseSessionDayRequest) => {
    if (!editingSessionDay) return
    
    try {
      setFormLoading(true)
      await updateSessionDay(editingSessionDay.id, data)
      setEditingSessionDay(null)
    } catch (error) {
      console.error('Failed to update session day:', error)
      throw error
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteSessionDay = async () => {
    if (!showDeleteConfirm) return

    try {
      await deleteSessionDay(showDeleteConfirm.id)
      setShowDeleteConfirm(null)
    } catch (error) {
      console.error('Failed to delete session day:', error)
    }
  }

  const getLocationName = (locationId: number) => {
    const location = locations.find(l => l.id === locationId)
    return location?.location_name || 'Unknown Location'
  }

  if (loading) return <LoadingSpinner />

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">Error loading session days: {error}</p>
        <Button
          onClick={refetch}
          className="mt-2"
          size="sm"
        >
          Try Again
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Session Days</h2>
          {(courseName || sessionName) && (
            <p className="text-sm text-gray-600 mt-1">
              {courseName && sessionName ? `${courseName} - ${sessionName}` : courseName || sessionName}
            </p>
          )}
        </div>
        <Button
          onClick={() => setShowForm(true)}
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Add Session Day</span>
        </Button>
      </div>

      {/* Session Days List */}
      {sessionDays.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No session days yet</h3>
          <p className="text-gray-500 mb-4">
            Get started by adding the first session day for this course session.
          </p>
          <Button
            onClick={() => setShowForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add First Session Day</span>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {sessionDays.map((sessionDay) => (
            <SessionDayCard
              key={sessionDay.id}
              sessionDay={sessionDay}
              locationName={getLocationName(sessionDay.location_id)}
              sessionName={sessionName}
              courseName={courseName}
              onEdit={setEditingSessionDay}
              onDelete={setShowDeleteConfirm}
            />
          ))}
        </div>
      )}

      {/* Create Session Day Modal */}
      <Modal
        isOpen={showForm}
        onClose={() => setShowForm(false)}
        title="Create Session Day"
        size="lg"
      >
        <ErrorBoundary>
          <SessionDayForm
            sessionId={sessionId}
            locations={locations}
            onSubmit={handleCreateSessionDay}
            onCancel={() => setShowForm(false)}
            loading={formLoading}
          />
        </ErrorBoundary>
      </Modal>

      {/* Edit Session Day Modal */}
      <Modal
        isOpen={!!editingSessionDay}
        onClose={() => setEditingSessionDay(null)}
        title="Edit Session Day"
        size="lg"
      >
        {editingSessionDay && (
          <SessionDayForm
            sessionDay={editingSessionDay}
            sessionId={sessionId}
            locations={locations}
            onSubmit={handleUpdateSessionDay}
            onCancel={() => setEditingSessionDay(null)}
            loading={formLoading}
          />
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(null)}
        title="Delete Session Day"
      >
        {showDeleteConfirm && (
          <div className="space-y-4">
            <p className="text-gray-600">
              Are you sure you want to delete Day {showDeleteConfirm.day_number}? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <Button
                variant="secondary"
                onClick={() => setShowDeleteConfirm(null)}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleDeleteSessionDay}
              >
                Delete Session Day
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}