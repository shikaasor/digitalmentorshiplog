# Digital Mentorship Log - Frontend

Next.js frontend application for the Digital Mentorship Log system.

## Technology Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3+
- **State Management**: Zustand
- **Form Handling**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Backend**: Supabase

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── dashboard/         # Dashboard pages
│   ├── mentorship-logs/   # Mentorship log pages
│   ├── auth/              # Authentication pages
│   ├── facilities/        # Facility management
│   └── users/             # User management
├── components/            # React components
│   ├── layouts/          # Layout components
│   ├── forms/            # Form components
│   ├── tables/           # Table components
│   ├── charts/           # Chart components
│   └── common/           # Common/shared components
├── lib/                   # Utilities and helpers
│   ├── services/         # API service functions
│   ├── stores/           # Zustand state stores
│   ├── api.ts            # API client configuration
│   ├── auth.ts           # Authentication utilities
│   └── hooks.ts          # Custom React hooks
├── types/                 # TypeScript type definitions
│   └── index.ts
├── styles/                # Global styles
│   └── globals.css
├── public/                # Static assets
├── .env.example          # Environment variables template
└── package.json          # Dependencies

```

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create a `.env.local` file:

```bash
cp .env.example .env.local
```

Update with your configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Key Features

### Authentication
- JWT-based authentication
- Login/logout functionality
- Protected routes
- Role-based access control

### Mentorship Logs
- Create and edit mentorship logs
- Planning section (pre-visit)
- Reporting section (post-visit)
- File attachments
- Submit for approval workflow

### Dashboard
- Role-specific dashboards (Mentor, Supervisor, Admin)
- KPI cards and metrics
- Performance charts
- Recent activity feed

### User Management
- User CRUD operations (admin only)
- Role assignment
- Facility assignments
- User profiles

### Facility Management
- Facility CRUD operations
- Performance tracking
- Assigned mentors
- Visit history

## Development Guidelines

### Component Structure

```typescript
// Example component structure
'use client' // For client components

import { useState } from 'react'

interface ComponentProps {
  prop1: string
  prop2?: number
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  const [state, setState] = useState()

  return (
    <div>
      {/* Component JSX */}
    </div>
  )
}
```

### API Calls

Use the centralized API client:

```typescript
import { apiClient } from '@/lib/api'

const response = await apiClient.get('/mentorship-logs')
```

### State Management

Use Zustand for global state:

```typescript
import { useAuthStore } from '@/lib/stores/auth.store'

const { user, login, logout } = useAuthStore()
```

### Form Handling

Use React Hook Form with Zod validation:

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

const { register, handleSubmit } = useForm({
  resolver: zodResolver(schema),
})
```

## Styling Guidelines

- Use Tailwind CSS utility classes
- Follow responsive design principles
- Maintain consistent spacing and colors
- Use the defined color palette in `tailwind.config.ts`

## Type Safety

- Always define TypeScript interfaces for props and data
- Import types from `@/types`
- Avoid using `any` type
- Use type guards for runtime type checking

## Contributing

1. Create a feature branch
2. Make changes with proper types
3. Test thoroughly
4. Submit pull request

## License

Proprietary - Digital Mentorship Log System
