# Scheduler Admin UI

Modern React TypeScript admin console for the Instructor Scheduling System.

## Features

- **Instructor Management**: Full CRUD operations for managing instructors
- **Modern UI**: Built with Tailwind CSS and Lucide React icons
- **Form Validation**: Zod schema validation with React Hook Form
- **Real-time Updates**: React Query for efficient data fetching and caching
- **Responsive Design**: Mobile-first responsive design
- **Type Safety**: Full TypeScript support throughout

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **React Hot Toast** - Toast notifications

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view in browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checks

## API Integration

The UI connects to the FastAPI backend running on `http://localhost:8000`. The Vite dev server proxies `/api` requests to the backend.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI components (Button, Input, etc.)
│   └── instructors/    # Instructor-specific components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API services
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── main.tsx           # Application entry point
```

## Development

### Adding New Features

1. Create types in `src/types/`
2. Add API methods to `src/services/api.ts`
3. Create React Query hooks in `src/hooks/`
4. Build UI components in `src/components/`
5. Create pages in `src/pages/`

### Styling

The app uses Tailwind CSS with a custom design system:
- Primary color: Blue (primary-500, primary-600, etc.)
- Font: Inter
- Icons: Lucide React

### Form Validation

Forms use Zod for schema validation with React Hook Form:
- Define schemas in component files
- Use `zodResolver` for form validation
- Display errors with proper styling