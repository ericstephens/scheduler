import { MapPin, MoreVertical, Edit, Trash2, CheckCircle, XCircle } from 'lucide-react'
import type { Location } from '@/types/location'
import { cn } from '@/utils/cn'
import { useState, useRef, useEffect } from 'react'
import Button from '@/components/ui/Button'

interface LocationCardProps {
  location: Location
  onEdit: (location: Location) => void
  onDelete: (location: Location) => void
  onUpdateStatus: (location: Location, active: boolean) => void
}

const getStatusColor = (active: boolean) => {
  return active 
    ? 'bg-green-100 text-green-800' 
    : 'bg-red-100 text-red-800'
}

const getStatusIcon = (active: boolean) => {
  return active 
    ? <CheckCircle className="h-4 w-4" />
    : <XCircle className="h-4 w-4" />
}

const getFullAddress = (location: Location) => {
  const parts = [
    location.address,
    location.city,
    location.state_province,
    location.postal_code
  ].filter(Boolean)
  
  return parts.length > 0 ? parts.join(', ') : null
}

export default function LocationCard({ 
  location, 
  onEdit, 
  onDelete, 
  onUpdateStatus
}: LocationCardProps) {
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
    onEdit(location)
  }

  const handleDeleteClick = () => {
    setShowDropdown(false)
    onDelete(location)
  }

  const handleStatusToggle = () => {
    setShowDropdown(false)
    onUpdateStatus(location, !location.active_status)
  }

  const fullAddress = getFullAddress(location)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          {/* Icon */}
          <div className="h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
            <MapPin className="h-6 w-6 text-primary-700" />
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {location.location_name}
              </h3>
              <span className={cn(
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                getStatusColor(location.active_status)
              )}>
                {getStatusIcon(location.active_status)}
                <span className="ml-1">{location.active_status ? 'ACTIVE' : 'INACTIVE'}</span>
              </span>
            </div>
            
            {fullAddress && (
              <div className="space-y-1">
                <div className="flex items-start text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="break-words">{fullAddress}</span>
                </div>
              </div>
            )}
            
            {location.notes && (
              <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                {location.notes}
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
                  onClick={handleStatusToggle}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                >
                  {location.active_status ? (
                    <>
                      <XCircle className="h-4 w-4 mr-3" />
                      Deactivate
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4 mr-3" />
                      Activate
                    </>
                  )}
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