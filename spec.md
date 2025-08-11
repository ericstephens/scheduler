# Instructor Scheduling Web Application Specification

## Project Overview
A web-based instructor scheduling system for an education business that manages contract instructors, courses, locations, and class session assignments. The application must be mobile-responsive and accessible via web browsers.

## Core Entities

### Instructors
- **Fields:**
  - ID (auto-generated)
  - First Name
  - Last Name
  - Email
  - Phone Number
  - Active Status (active/inactive)
  - Created Date
  - Notes (optional)

### Courses
- **Fields:**
  - ID (auto-generated)
  - Course Name
  - Course Code (unique identifier)
  - Description
  - Duration (in days)
  - Active Status (active/inactive)
  - Created Date

### Locations
- **Fields:**
  - ID (auto-generated)
  - Location Name
  - Address
  - City
  - State/Province
  - Postal Code
  - Location Type (classroom, range, online, etc.)
  - Capacity
  - Active Status (active/inactive)
  - Notes (optional)

### Instructor Course Ratings
- **Fields:**
  - ID (auto-generated)
  - Instructor ID (foreign key)
  - Course ID (foreign key)
  - Rating (enum: "observe", "co-teach", "cleared")
  - Date Assigned
  - Date Updated
  - Notes (optional)

### Class Sessions
- **Fields:**
  - ID (auto-generated)
  - Course ID (foreign key)
  - Session Name/Title
  - Start Date
  - End Date
  - Status (scheduled, in-progress, completed, cancelled)
  - Total Students (optional)
  - Notes (optional)

### Session Days
- **Fields:**
  - ID (auto-generated)
  - Session ID (foreign key)
  - Day Number (1, 2, 3, etc.)
  - Date
  - Location ID (foreign key)
  - Start Time
  - End Time
  - Session Type (half-day, full-day)

### Instructor Assignments
- **Fields:**
  - ID (auto-generated)
  - Session Day ID (foreign key)
  - Instructor ID (foreign key)
  - Assignment Type (half-day, full-day)
  - Assignment Status (assigned, confirmed, completed, cancelled)
  - Pay Eligible (boolean - true only if instructor is "cleared" for the course)
  - Created Date
  - Notes (optional)

## Functional Requirements

### 1. Instructor Management
- Add, edit, delete, and view instructors
- Mark instructors as active/inactive
- Search and filter instructors by name, status, or course clearance
- Mobile-friendly instructor list with swipe actions

### 2. Course Management
- Add, edit, delete, and view courses
- Mark courses as active/inactive
- Search and filter courses by name, code, or status
- View which instructors are rated for each course

### 3. Location Management
- Add, edit, delete, and view locations
- Mark locations as active/inactive
- Search and filter locations by name, type, or city
- View location capacity and details

### 4. Instructor Course Rating Management
- Assign ratings (observe, co-teach, cleared) to instructor-course combinations
- Update existing ratings
- View rating history for each instructor-course pair
- Filter instructors by course and rating level
- Bulk rating updates for multiple instructors

### 5. Class Session Management
- Create new class sessions with multiple days
- Assign different locations to different days of the same session
- Edit session details and dates
- View session overview with all days and assignments
- Cancel or reschedule sessions

### 6. Assignment Management
- Assign instructors to specific session days
- Support both half-day and full-day assignments
- Prevent assignment of instructors not "cleared" for the course (with warning)
- Show pay eligibility status for each assignment
- View instructor availability conflicts
- Bulk assignment capabilities
- Assignment confirmation workflow

### 7. Reporting and Views
- Instructor schedule view (calendar format)
- Course schedule overview
- Pay-eligible assignments report
- Instructor utilization reports
- Location utilization reports
- Mobile-optimized dashboard

## Technical Requirements

### Frontend
- **Framework:** React with TypeScript
- **Styling:** Tailwind CSS for responsive design
- **Mobile:** Progressive Web App (PWA) capabilities
- **State Management:** React Context or Redux Toolkit
- **Routing:** React Router
- **UI Components:** Modern component library (Headless UI, Radix, or similar)
- **Forms:** React Hook Form with validation
- **Date/Time:** Date picker components for scheduling

### Backend
- **Framework:** Node.js with Express or Next.js API routes
- **Database:** PostgreSQL with Prisma ORM
- **Authentication:** JWT-based authentication system
- **API:** RESTful API design
- **Validation:** Server-side input validation
- **Error Handling:** Comprehensive error handling and logging

### Database Schema
- Relational database with proper foreign key relationships
- Indexes on frequently queried fields
- Soft deletes for maintaining data integrity
- Audit trail for critical changes

### Mobile Responsiveness
- Touch-friendly interface elements
- Responsive grid layouts
- Collapsible navigation menu
- Swipe gestures for mobile actions
- Optimized for tablets and smartphones
- Fast loading times with lazy loading

## User Interface Requirements

### Navigation
- Clean, intuitive navigation bar
- Breadcrumb navigation for deep pages
- Quick access to common functions
- Mobile hamburger menu

### Dashboard
- Overview of upcoming sessions
- Quick stats (active instructors, scheduled sessions, etc.)
- Recent activity feed
- Quick action buttons

### List Views
- Sortable columns
- Search and filter capabilities
- Pagination for large datasets
- Bulk action checkboxes
- Export functionality

### Forms
- Clear field labels and validation messages
- Auto-save for long forms
- Confirmation dialogs for destructive actions
- Loading states for async operations

### Calendar/Schedule Views
- Monthly, weekly, and daily views
- Color-coded assignments
- Drag-and-drop scheduling (optional)
- Conflict highlighting

## Security Requirements
- User authentication and authorization
- Role-based access control (admin, scheduler, instructor view)
- Input sanitization and validation
- HTTPS encryption
- Session management
- Data backup and recovery procedures

## Performance Requirements
- Page load times under 3 seconds
- Smooth animations and transitions
- Efficient database queries
- Caching for frequently accessed data
- Offline capability for viewing schedules (PWA)

## Integration Considerations
- API endpoints for potential future integrations
- Export capabilities (CSV, PDF reports)
- Email notifications for assignments (future enhancement)
- Calendar integration (Google Calendar, Outlook) (future enhancement)

## Deployment
- Cloud hosting (Vercel, Netlify, or similar)
- Environment configuration for development, staging, and production
- Automated database migrations
- Monitoring and logging setup

## Future Enhancements (Phase 2)
- Email/SMS notifications
- Instructor self-service portal
- Time tracking integration
- Payment processing integration
- Advanced reporting and analytics
- Mobile app (native)
- Calendar sync capabilities

## Development Priorities
1. Core data models and database setup
2. Basic CRUD operations for all entities
3. Session and assignment management
4. Mobile-responsive UI
5. Rating and pay eligibility logic
6. Reporting and dashboard features
7. Authentication and user management
8. Testing and deployment

This specification provides a comprehensive foundation for building a robust instructor scheduling system that can scale with your education business needs.