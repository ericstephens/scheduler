import { Calendar, Clock, MapPin, MoreVertical, Edit, Trash2 } from 'lucide-react'
import type { CourseSessionDay } from '@/types/courseSession'
import { SessionType } from '@/types/courseSession'
import { formatDate } from '@/utils/formatters'
import { cn } from '@/utils/cn'
import { useState, useRef, useEffect } from 'react'
import Button from '@/components/ui/Button'

interface SessionDayCardProps {
  sessionDay: CourseSessionDay
  onEdit: (sessionDay: CourseSessionDay) => void
  onDelete: (sessionDay: CourseSessionDay) => void
  locationName?: string
  sessionName?: string
  courseName?: string
}

const getSessionTypeIcon = (sessionType: SessionType) => {
  switch (sessionType) {
    case SessionType.HALF_DAY:
      return <Clock className="h-4 w-4" />
    case SessionType.FULL_DAY:
      return <Calendar className="h-4 w-4" />
    default:
      return <Clock className="h-4 w-4" />
  }
}

const getSessionTypeColor = (sessionType: SessionType) => {
  switch (sessionType) {
    case SessionType.HALF_DAY:
      return 'bg-blue-100 text-blue-800'
    case SessionType.FULL_DAY:
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatTime = (timeStr: string) => {
  try {
    const [hours, minutes] = timeStr.split(':')
    const hour = parseInt(hours, 10)
    const minute = parseInt(minutes, 10)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour
    return `${displayHour}:${minute.toString().padStart(2, '0')} ${ampm}`
  } catch {
    return timeStr
  }
}

export default function SessionDayCard({ 
  sessionDay, 
  onEdit, 
  onDelete, 
  locationName,
  sessionName,
  courseName
}: SessionDayCardProps) {
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
    onEdit(sessionDay)
  }

  const handleDeleteClick = () => {
    setShowDropdown(false)
    onDelete(sessionDay)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          {/* Day Number Badge */}
          <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-lg font-bold text-primary-700">
              {sessionDay.day_number}
            </span>
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                Day {sessionDay.day_number}
              </h3>
              <span className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                getSessionTypeColor(sessionDay.session_type)
              )}>
                {getSessionTypeIcon(sessionDay.session_type)}
                <span className="ml-1">
                  {sessionDay.session_type === SessionType.HALF_DAY ? 'Half Day' : 'Full Day'}
                </span>
              </span>
            </div>
            
            {(courseName || sessionName) && (
              <div className="mb-2">
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                  {courseName && sessionName ? `${courseName} - ${sessionName}` : courseName || sessionName}
                </span>
              </div>
            )}
            
            <div className="space-y-1">
              <div className="flex items-center text-sm text-gray-600">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(sessionDay.date)}
              </div>
              
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="h-4 w-4 mr-2" />
                {formatTime(sessionDay.start_time)} - {formatTime(sessionDay.end_time)}
              </div>
              
              {locationName && (
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2" />
                  {locationName}
                </div>
              )}
            </div>
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