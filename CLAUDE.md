# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Instructor Scheduling Web Application** - A mobile-responsive web-based system for managing contract instructors, courses, locations, and class session assignments for an education business.

## Technology Stack

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS for responsive design
- **Mobile**: Progressive Web App (PWA) capabilities
- **State Management**: React Context or Redux Toolkit
- **Routing**: React Router
- **UI Components**: Modern component library (Headless UI, Radix)
- **Forms**: React Hook Form with validation
- **Date/Time**: Date picker components for scheduling

### Backend
- **Framework**: Node.js with Express or Next.js API routes
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT-based authentication system
- **API**: RESTful API design
- **Validation**: Server-side input validation
- **Container Runtime**: Podman (not Docker)
- **Management**: manage.sh script for all stop/start/restart operations

## Project Structure

```
scheduler/
├── src/
│   ├── frontend/      # React TypeScript frontend
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   └── test/      # Frontend tests
│   ├── api/           # Node.js API layer
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── utils/
│   │   └── test/      # API tests
│   └── database/      # Database schema & migrations
│       ├── prisma/
│       ├── migrations/
│       └── seeds/
├── docker-compose.yml # For PostgreSQL container
└── manage.sh          # Management script
```

## Core Data Models

### Primary Entities
1. **Instructors** - Contract instructor management
2. **Courses** - Course catalog with codes and descriptions
3. **Locations** - Training locations with capacity info
4. **Instructor Course Ratings** - Rating system (observe, co-teach, cleared)
5. **Class Sessions** - Multi-day training sessions
6. **Session Days** - Individual days within sessions
7. **Instructor Assignments** - Daily instructor assignments with pay eligibility

## Development Rules

### Architecture Constraints
- **Separation of Concerns**: Frontend → API → Database (no direct frontend-to-database access)
- **No Circular Dependencies**: Database models should not import from API controllers
- **All code should be created/modified within src/ and its subdirectories**
- **Pay Eligibility Rule**: Only instructors "cleared" for a course are pay-eligible

### Database
- **PostgreSQL only** - no SQLite anywhere in the codebase
- Run PostgreSQL in local podman container
- Use Prisma ORM for database operations
- Implement soft deletes for data integrity
- Include audit trails for critical changes

### API Layer
- RESTful API design with proper HTTP status codes
- JWT-based authentication system
- Server-side input validation and sanitization
- Comprehensive error handling and logging
- Generate unit tests for all API endpoints

### Frontend
- Mobile-first responsive design with Tailwind CSS
- Progressive Web App (PWA) capabilities
- React Hook Form for form validation
- No direct database access - all data through API
- Touch-friendly interface with swipe gestures
- Unit tests for components and user interactions

### Container Management (Podman)
Use podman commands instead of docker:
- `podman` instead of `docker`
- `podman-compose` instead of `docker-compose`  
- `podman machine` instead of `docker machine`
- All machine operations: start, stop, restart, rm, inspect, list

### Testing Philosophy
- **No mocking** - all tests should use real implementations
- Generate comprehensive unit tests for all layers
- Use appropriate testing frameworks (Jest/React Testing Library for frontend)
- Test database operations against real PostgreSQL instance

### Development Workflow
- Use `manage.sh` script for all stop/start/restart operations
- Focus on small, incremental changes and commits
- Test each layer independently with its own test suite
- Mobile-responsive testing on multiple screen sizes

## Key Business Logic

### Rating System
- **observe**: Instructor can observe classes (not pay-eligible)
- **co-teach**: Instructor can co-teach (not pay-eligible)
- **cleared**: Instructor fully qualified (pay-eligible)

### Assignment Rules
- Prevent assignment of non-cleared instructors (show warning)
- Support half-day and full-day assignments
- Track assignment status (assigned, confirmed, completed, cancelled)
- Highlight scheduling conflicts

### Mobile Experience
- Touch-friendly interface elements
- Responsive grid layouts
- Collapsible navigation menu
- Fast loading with lazy loading
- Offline capability for viewing schedules

## Commands to Remember

- **Development**: `npm run dev` (frontend), `npm run start:dev` (api)
- **Testing**: `npm test` (appropriate test runner per layer)
- **Database**: `npx prisma migrate dev`, `npx prisma studio`
- **Management**: `./manage.sh start|stop|restart`
- **Container**: `podman-compose up -d` for PostgreSQL
- memory