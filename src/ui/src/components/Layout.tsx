import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Users, Calendar, MapPin, Settings, BookOpen } from 'lucide-react'
import { cn } from '@/utils/cn'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Instructors', href: '/instructors', icon: Users },
  { name: 'Courses', href: '/courses', icon: BookOpen },
  { name: 'Course Sessions', href: '/sessions', icon: Calendar },
  { name: 'Locations', href: '/locations', icon: MapPin },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 items-center px-6 border-b border-gray-200">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <Calendar className="h-5 w-5 text-white" />
            </div>
            <span className="ml-3 text-lg font-semibold text-gray-900">
              Scheduler Admin
            </span>
          </div>
        </div>
        
        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    isActive
                      ? 'bg-primary-50 border-primary-500 text-primary-700'
                      : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                    'group border-l-4 px-3 py-2 flex items-center text-sm font-medium transition-colors'
                  )}
                >
                  <Icon
                    className={cn(
                      isActive
                        ? 'text-primary-500'
                        : 'text-gray-400 group-hover:text-gray-500',
                      'mr-3 h-5 w-5 transition-colors'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  )
}