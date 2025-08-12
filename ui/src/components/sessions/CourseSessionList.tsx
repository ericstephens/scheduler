import { useState } from 'react'
import { Search, Plus, Calendar, Filter } from 'lucide-react'
import type { CourseSession } from '@/types/courseSession'
import { SessionStatus } from '@/types/courseSession'
import CourseSessionCard from './CourseSessionCard'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface CourseSessionListProps {
  courseSessions: CourseSession[]
  onCreateNew: () => void
  onEdit: (courseSession: CourseSession) => void
  onDelete: (courseSession: CourseSession) => void
  onUpdateStatus: (courseSession: CourseSession, status: SessionStatus) => void
  isLoading?: boolean
  courses: { id: number; course_name: string; course_code: string }[]
}

export default function CourseSessionList({
  courseSessions,
  onCreateNew,
  onEdit,
  onDelete,
  onUpdateStatus,
  isLoading = false,
  courses = [],
}: CourseSessionListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<SessionStatus | 'all'>('all')

  const filteredSessions = courseSessions.filter((session) => {
    const searchTerm = searchQuery.toLowerCase()
    const matchesSearch = (
      session.session_name.toLowerCase().includes(searchTerm) ||
      session.notes?.toLowerCase().includes(searchTerm)
    )
    
    const matchesStatus = statusFilter === 'all' || session.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  // Get course info for each session
  const getSessionWithCourseInfo = (session: CourseSession) => {
    const course = courses.find(c => c.id === session.course_id)
    return {
      ...session,
      courseName: course?.course_name,
      courseCode: course?.course_code,
    }
  }

  const statusCounts = {
    total: courseSessions.length,
    scheduled: courseSessions.filter(s => s.status === SessionStatus.SCHEDULED).length,
    in_progress: courseSessions.filter(s => s.status === SessionStatus.IN_PROGRESS).length,
    completed: courseSessions.filter(s => s.status === SessionStatus.COMPLETED).length,
    cancelled: courseSessions.filter(s => s.status === SessionStatus.CANCELLED).length,
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading course sessions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Course Sessions</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage training sessions and schedules
          </p>
        </div>
        
        <Button onClick={onCreateNew} className="flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add Session
        </Button>
      </div>

      {/* Stats and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <Calendar className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-900">
                {statusCounts.total} Total Sessions
              </span>
            </div>
            <div className="text-sm text-gray-600">
              {statusCounts.scheduled} Scheduled, {statusCounts.in_progress} In Progress, 
              {statusCounts.completed} Completed, {statusCounts.cancelled} Cancelled
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search sessions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as SessionStatus | 'all')}
              className="block rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value={SessionStatus.SCHEDULED}>Scheduled</option>
              <option value={SessionStatus.IN_PROGRESS}>In Progress</option>
              <option value={SessionStatus.COMPLETED}>Completed</option>
              <option value={SessionStatus.CANCELLED}>Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {filteredSessions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery || statusFilter !== 'all' ? 'No matching sessions' : 'No sessions found'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your search terms or filters' 
              : 'Get started by creating your first training session'
            }
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Add First Session
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredSessions.map((session) => {
            const sessionWithCourse = getSessionWithCourseInfo(session)
            return (
              <CourseSessionCard
                key={session.id}
                courseSession={session}
                onEdit={onEdit}
                onDelete={onDelete}
                onUpdateStatus={onUpdateStatus}
                courseName={sessionWithCourse.courseName}
                courseCode={sessionWithCourse.courseCode}
              />
            )
          })}
        </div>
      )}

      {(searchQuery || statusFilter !== 'all') && filteredSessions.length > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {filteredSessions.length} of {courseSessions.length} sessions
        </div>
      )}
    </div>
  )
}