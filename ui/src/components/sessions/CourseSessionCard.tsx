import { Calendar, Clock, MoreVertical, Edit, Trash2, Play, CheckCircle, XCircle } from 'lucide-react'
import type { CourseSession } from '@/types/courseSession'
import { SessionStatus } from '@/types/courseSession'
import { formatDate } from '@/utils/formatters'
import { cn } from '@/utils/cn'
import { useState, useRef, useEffect } from 'react'
import Button from '@/components/ui/Button'

interface CourseSessionCardProps {
  courseSession: CourseSession
  onEdit: (courseSession: CourseSession) => void
  onDelete: (courseSession: CourseSession) => void
  onUpdateStatus: (courseSession: CourseSession, status: SessionStatus) => void
  courseName?: string
  courseCode?: string
}

const getStatusIcon = (status: SessionStatus) => {
  switch (status) {
    case SessionStatus.SCHEDULED:
      return <Calendar className="h-4 w-4" />
    case SessionStatus.IN_PROGRESS:
      return <Play className="h-4 w-4" />
    case SessionStatus.COMPLETED:
      return <CheckCircle className="h-4 w-4" />
    case SessionStatus.CANCELLED:
      return <XCircle className="h-4 w-4" />
    default:
      return <Calendar className="h-4 w-4" />
  }
}

const getStatusColor = (status: SessionStatus) => {
  switch (status) {
    case SessionStatus.SCHEDULED:
      return 'bg-blue-100 text-blue-800'
    case SessionStatus.IN_PROGRESS:
      return 'bg-green-100 text-green-800'
    case SessionStatus.COMPLETED:
      return 'bg-gray-100 text-gray-800'
    case SessionStatus.CANCELLED:
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusActions = (status: SessionStatus) => {
  const actions = []
  
  switch (status) {
    case SessionStatus.SCHEDULED:
      actions.push(
        { label: 'Start Session', status: SessionStatus.IN_PROGRESS, icon: Play },
        { label: 'Cancel Session', status: SessionStatus.CANCELLED, icon: XCircle }
      )
      break
    case SessionStatus.IN_PROGRESS:
      actions.push(
        { label: 'Complete Session', status: SessionStatus.COMPLETED, icon: CheckCircle },
        { label: 'Cancel Session', status: SessionStatus.CANCELLED, icon: XCircle }
      )
      break
    case SessionStatus.COMPLETED:
    case SessionStatus.CANCELLED:
      actions.push(
        { label: 'Reschedule', status: SessionStatus.SCHEDULED, icon: Calendar }
      )
      break
  }
  
  return actions
}

export default function CourseSessionCard({ 
  courseSession, 
  onEdit, 
  onDelete, 
  onUpdateStatus,
  courseName,
  courseCode
}: CourseSessionCardProps) {
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleEditClick = () => {
    setShowDropdown(false)
    onEdit(courseSession)
  }

  const handleDeleteClick = () => {
    setShowDropdown(false)
    onDelete(courseSession)
  }

  const handleStatusChange = (status: SessionStatus) => {
    setShowDropdown(false)
    onUpdateStatus(courseSession, status)
  }

  const statusActions = getStatusActions(courseSession.status)
  const startDate = new Date(courseSession.start_date)
  const endDate = new Date(courseSession.end_date)
  const durationDays = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          {/* Icon */}
          <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
            <Calendar className="h-6 w-6 text-primary-700" />
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {courseSession.session_name}
              </h3>
              <span className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                getStatusColor(courseSession.status)
              )}>
                {getStatusIcon(courseSession.status)}
                <span className="ml-1">{courseSession.status.replace('_', ' ').toUpperCase()}</span>
              </span>
            </div>
            
            {(courseName || courseCode) && (
              <div className="mb-2">
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                  {courseCode && `${courseCode} - `}{courseName}
                </span>
              </div>
            )}
            
            <div className="space-y-1">
              <div className="flex items-center text-sm text-gray-600">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(courseSession.start_date)} - {formatDate(courseSession.end_date)}
              </div>
              
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="h-4 w-4 mr-2" />
                {durationDays} day{durationDays !== 1 ? 's' : ''}
              </div>
            </div>
            
            {courseSession.notes && (
              <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                {courseSession.notes}
              </div>
            )}
          </div>
        </div>
        
        {/* Actions Menu */}
        <div className="relative" ref={dropdownRef}>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowDropdown(!showDropdown)}
            className="h-8 w-8 p-0"
          >
            <MoreVertical className="h-4 w-4" />
          </Button>
          
          {showDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
              <div className="py-1">
                <button
                  onClick={handleEditClick}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                >
                  <Edit className="h-4 w-4 mr-3" />
                  Edit
                </button>
                
                {statusActions.map((action, index) => {
                  const Icon = action.icon
                  return (
                    <button
                      key={index}
                      onClick={() => handleStatusChange(action.status)}
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                    >
                      <Icon className="h-4 w-4 mr-3" />
                      {action.label}
                    </button>
                  )
                })}
                
                <button
                  onClick={handleDeleteClick}
                  className="flex items-center px-4 py-2 text-sm text-red-700 hover:bg-red-50 w-full text-left"
                >
                  <Trash2 className="h-4 w-4 mr-3" />
                  Delete
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}