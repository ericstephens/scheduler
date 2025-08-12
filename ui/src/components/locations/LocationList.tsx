import { useState } from 'react'
import { Search, Plus, MapPin, Filter } from 'lucide-react'
import type { Location } from '@/types/location'
import LocationCard from './LocationCard'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

interface LocationListProps {
  locations: Location[]
  onCreateNew: () => void
  onEdit: (location: Location) => void
  onDelete: (location: Location) => void
  onUpdateStatus: (location: Location, active: boolean) => void
  isLoading?: boolean
}

export default function LocationList({
  locations,
  onCreateNew,
  onEdit,
  onDelete,
  onUpdateStatus,
  isLoading = false,
}: LocationListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all')

  const filteredLocations = locations.filter((location) => {
    const searchTerm = searchQuery.toLowerCase()
    const matchesSearch = (
      location.location_name.toLowerCase().includes(searchTerm) ||
      location.address?.toLowerCase().includes(searchTerm) ||
      location.city?.toLowerCase().includes(searchTerm) ||
      location.state_province?.toLowerCase().includes(searchTerm) ||
      location.notes?.toLowerCase().includes(searchTerm)
    )
    
    const matchesStatus = 
      statusFilter === 'all' || 
      (statusFilter === 'active' && location.active_status) ||
      (statusFilter === 'inactive' && !location.active_status)
    
    return matchesSearch && matchesStatus
  })

  const statusCounts = {
    total: locations.length,
    active: locations.filter(l => l.active_status).length,
    inactive: locations.filter(l => !l.active_status).length,
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading locations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Locations</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage training locations and facilities
          </p>
        </div>
        
        <Button onClick={onCreateNew} className="flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add Location
        </Button>
      </div>

      {/* Stats and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <MapPin className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-900">
                {statusCounts.total} Total Locations
              </span>
            </div>
            <div className="text-sm text-gray-600">
              {statusCounts.active} Active, {statusCounts.inactive} Inactive
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
              placeholder="Search locations..."
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
              onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive')}
              className="block rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {filteredLocations.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery || statusFilter !== 'all' ? 'No matching locations' : 'No locations found'}
          </h3>
          <p className="text-gray-600 mb-6">
            {searchQuery || statusFilter !== 'all'
              ? 'Try adjusting your search terms or filters' 
              : 'Get started by adding your first training location'
            }
          </p>
          {!searchQuery && statusFilter === 'all' && (
            <Button onClick={onCreateNew}>
              <Plus className="h-4 w-4 mr-2" />
              Add First Location
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredLocations.map((location) => (
            <LocationCard
              key={location.id}
              location={location}
              onEdit={onEdit}
              onDelete={onDelete}
              onUpdateStatus={onUpdateStatus}
            />
          ))}
        </div>
      )}

      {(searchQuery || statusFilter !== 'all') && filteredLocations.length > 0 && (
        <div className="text-sm text-gray-600 text-center">
          Showing {filteredLocations.length} of {locations.length} locations
        </div>
      )}
    </div>
  )
}