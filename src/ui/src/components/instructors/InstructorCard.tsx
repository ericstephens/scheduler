import { User, Phone, Mail, MoreVertical, Edit, Trash2 } from 'lucide-react'
import type { Instructor } from '@/types/instructor'
import { formatDate, formatPhoneNumber, getInitials } from '@/utils/formatters'
import { cn } from '@/utils/cn'
import { useState, useRef, useEffect } from 'react'
import Button from '@/components/ui/Button'

interface InstructorCardProps {
  instructor: Instructor
  onEdit: (instructor: Instructor) => void
  onDelete: (instructor: Instructor) => void
  onToggleStatus: (instructor: Instructor) => void
}

export default function InstructorCard({ 
  instructor, 
  onEdit, 
  onDelete, 
  onToggleStatus 
}: InstructorCardProps) {
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
    onEdit(instructor)
  }

  const handleDeleteClick = () => {
    setShowDropdown(false)
    onDelete(instructor)
  }

  const handleToggleStatusClick = () => {
    setShowDropdown(false)
    onToggleStatus(instructor)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          {/* Avatar */}
          <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-700 font-semibold">
              {getInitials(instructor.first_name, instructor.last_name)}
            </span>
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {instructor.first_name} {instructor.last_name}
              </h3>
              {instructor.call_sign && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {instructor.call_sign}
                </span>
              )}
              <span className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                instructor.active_status
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              )}>
                {instructor.active_status ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <div className="mt-2 space-y-1">
              <div className="flex items-center text-sm text-gray-600">
                <Mail className="h-4 w-4 mr-2" />
                <a 
                  href={`mailto:${instructor.email}`}
                  className="hover:text-primary-600 transition-colors"
                >
                  {instructor.email}
                </a>
              </div>
              
              {instructor.phone_number && (
                <div className="flex items-center text-sm text-gray-600">
                  <Phone className="h-4 w-4 mr-2" />
                  <a 
                    href={`tel:${instructor.phone_number}`}
                    className="hover:text-primary-600 transition-colors"
                  >
                    {formatPhoneNumber(instructor.phone_number)}
                  </a>
                </div>
              )}
            </div>
            
            <div className="mt-3 text-xs text-gray-500">
              Created {formatDate(instructor.created_date)}
            </div>
            
            {instructor.notes && (
              <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                {instructor.notes}
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
                
                <button
                  onClick={handleToggleStatusClick}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                >
                  <User className="h-4 w-4 mr-3" />
                  {instructor.active_status ? 'Deactivate' : 'Activate'}
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