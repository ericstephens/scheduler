import { useState } from 'react'
import { Search, Plus, Users, Filter } from 'lucide-react'
import type { Instructor } from '@/types/instructor'
import InstructorCard from './InstructorCard'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface InstructorListProps {
  instructors: Instructor[]
  onCreateNew: () => void
  onEdit: (instructor: Instructor) => void
  onDelete: (instructor: Instructor) => void
  onToggleStatus: (instructor: Instructor) => void
  isLoading?: boolean
  showInactive?: boolean
  onToggleInactive: (show: boolean) => void
}

export default function InstructorList({
  instructors,
  onCreateNew,
  onEdit,
  onDelete,
  onToggleStatus,
  isLoading = false,
  showInactive = false,
  onToggleInactive,
}: InstructorListProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredInstructors = instructors.filter((instructor) => {
    const searchTerm = searchQuery.toLowerCase()
    return (
      instructor.first_name.toLowerCase().includes(searchTerm) ||
      instructor.last_name.toLowerCase().includes(searchTerm) ||
      instructor.email.toLowerCase().includes(searchTerm) ||
      instructor.call_sign?.toLowerCase().includes(searchTerm) ||
      instructor.phone_number?.includes(searchTerm)
    )
  })

  const activeCount = instructors.filter(i => i.active_status).length
  const inactiveCount = instructors.filter(i => !i.active_status).length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading instructors...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Instructors</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your instructor database
          </p>
        </div>
        
        <Button onClick={onCreateNew} className="flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add Instructor
        </Button>
      </div>

      {/* Stats and Filters */}
      <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-6">
          <div className="flex items-center">
            <Users className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-900">
              {instructors.length} Total
            </span>
          </div>
          <div className="text-sm text-gray-600">
            {activeCount} Active, {inactiveCount} Inactive
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant={showInactive ? 'default' : 'outline'}
            size="sm"
            onClick={() => onToggleInactive(!showInactive)}
            className="flex items-center"
          >
            <Filter className="h-4 w-4 mr-2" />
            {showInactive ? 'Show Active Only' : 'Show All'}
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          placeholder="Search instructors..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Results */}
      {filteredInstructors.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery ? 'No matching instructors' : 'No instructors found'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery 
              ? 'Try adjusting your search terms' 
              : 'Get started by adding your first instructor'
            }
          </p>
          {!searchQuery && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Add First Instructor
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredInstructors.map((instructor) => (
            <InstructorCard
              key={instructor.id}
              instructor={instructor}
              onEdit={onEdit}
              onDelete={onDelete}
              onToggleStatus={onToggleStatus}
            />
          ))}
        </div>
      )}

      {searchQuery && filteredInstructors.length > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {filteredInstructors.length} of {instructors.length} instructors
        </div>
      )}
    </div>
  )
}