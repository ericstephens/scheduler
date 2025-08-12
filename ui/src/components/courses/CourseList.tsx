import { useState } from 'react'
import { Search, Plus, BookOpen, Filter } from 'lucide-react'
import type { Course } from '@/types/course'
import CourseCard from './CourseCard'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface CourseListProps {
  courses: Course[]
  onCreateNew: () => void
  onEdit: (course: Course) => void
  onDelete: (course: Course) => void
  onToggleStatus: (course: Course) => void
  isLoading?: boolean
  showInactive?: boolean
  onToggleInactive: (show: boolean) => void
}

export default function CourseList({
  courses,
  onCreateNew,
  onEdit,
  onDelete,
  onToggleStatus,
  isLoading = false,
  showInactive = false,
  onToggleInactive,
}: CourseListProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredCourses = courses.filter((course) => {
    const searchTerm = searchQuery.toLowerCase()
    return (
      course.course_name.toLowerCase().includes(searchTerm) ||
      course.course_code.toLowerCase().includes(searchTerm) ||
      course.description?.toLowerCase().includes(searchTerm)
    )
  })

  const activeCount = courses.filter(c => c.active_status).length
  const inactiveCount = courses.filter(c => !c.active_status).length

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading courses...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Courses</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your course catalog
          </p>
        </div>
        
        <Button onClick={onCreateNew} className="flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add Course
        </Button>
      </div>

      {/* Stats and Filters */}
      <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center space-x-6">
          <div className="flex items-center">
            <BookOpen className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-sm font-medium text-gray-900">
              {courses.length} Total
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
          placeholder="Search courses..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Results */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery ? 'No matching courses' : 'No courses found'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery 
              ? 'Try adjusting your search terms' 
              : 'Get started by adding your first course'
            }
          </p>
          {!searchQuery && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Add First Course
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onEdit={onEdit}
              onDelete={onDelete}
              onToggleStatus={onToggleStatus}
            />
          ))}
        </div>
      )}

      {searchQuery && filteredCourses.length > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {filteredCourses.length} of {courses.length} courses
        </div>
      )}
    </div>
  )
}