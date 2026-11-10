# Task Manager Frontend

A modern, responsive, and polished frontend for the Task Manager REST API built with **React 18**, **Vite**, **TypeScript**, **Tailwind CSS**, **React Router v6**, **TanStack Query (React Query)**, **React Hook Form**, and **Zod**.

---

## Features

- **Authentication & Authorization**:
  - Secure registration and login with real-time inline validation (`EmailStr`, password $\ge 8$ chars, username $3-30$ alphanumeric/underscore).
  - Server error feedback for duplicate accounts (`409 Conflict`) and bad credentials (`401 Unauthorized`).
  - Form-encoded login (`application/x-www-form-urlencoded`) compliant with OAuth2.
  - JWT token stored in `localStorage` and automatically attached via Axios interceptors.
  - Automatic session expiration detection with redirection and notifications.
  - Route guards: `ProtectedRoute` for private dashboard, redirecting authenticated users away from `/login` and `/register`.
- **Task Management**:
  - Full CRUD operations with instant UI updates via TanStack Query invalidation.
  - Quick status cycle: one-click status badge cycling (`todo` $\rightarrow$ `in_progress` $\rightarrow$ `done` $\rightarrow$ `todo`).
  - Partial updates using `PATCH /tasks/{id}`, sending only changed fields.
  - Safe deletion with an accessible, keyboard-closable `ConfirmDialog`.
  - Overdue date detection highlighting overdue unfinished tasks in red.
- **Filters, Search & Pagination**:
  - Live 300ms debounced search on task title.
  - Status and priority dropdown filters with a one-click Reset button.
  - Multi-field sorting by `created_at`, `due_date`, or `priority` in `asc` or `desc` order.
  - Dynamic pagination controls with items range indicator and configurable page size (10, 20, 50).
- **Summary Dashboard Metrics**:
  - Top metric cards displaying live counts for Total Tasks, To Do, In Progress, and Completed tasks.
- **UI / UX Polish**:
  - Mobile-first responsive layout with Tailwind CSS.
  - Dark mode with persistent `localStorage` theme toggle.
  - Micro-interactions, loading spinners, empty states with call-to-action, error recovery with retry button, and toast notifications (`react-hot-toast`).
  - Accessible dialogs supporting Escape key dismissal and ARIA attributes.

---

## Directory Structure

```
frontend/
├── src/
│   ├── api/                   # Axios client instance, auth API, tasks API
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   └── tasks.ts
│   ├── context/
│   │   └── AuthContext.tsx    # User state, login, register, logout
│   ├── hooks/
│   │   ├── useAuth.ts         # Hook to access AuthContext
│   │   └── useTasks.ts        # TanStack Query hooks for tasks CRUD
│   ├── components/
│   │   ├── ConfirmDialog.tsx  # Accessible deletion confirmation modal
│   │   ├── EmptyState.tsx     # Zero-data screen with CTA
│   │   ├── FilterBar.tsx      # Search, filter, sorting, and reset controls
│   │   ├── Navbar.tsx         # Brand header, user status, dark mode toggle, logout
│   │   ├── Pagination.tsx     # Next/prev navigation and page sizing
│   │   ├── PriorityBadge.tsx  # Priority badges (low=slate, medium=amber, high=red)
│   │   ├── ProtectedRoute.tsx # Route guard redirecting unauthenticated users
│   │   ├── Spinner.tsx        # Reusable loading indicator
│   │   ├── StatusBadge.tsx    # Status badges (todo=gray, in_progress=blue, done=green)
│   │   ├── TaskCard.tsx       # Individual task display card
│   │   └── TaskModal.tsx      # Task creation & edit modal with Zod validation
│   ├── pages/
│   │   ├── DashboardPage.tsx  # Primary task management dashboard
│   │   ├── LoginPage.tsx      # Sign in page
│   │   ├── NotFoundPage.tsx   # 404 page
│   │   └── RegisterPage.tsx   # Account registration page
│   ├── types/
│   │   └── index.ts           # Strict TypeScript contracts matching backend API
│   ├── App.tsx                # App root with QueryClientProvider & BrowserRouter
│   ├── main.tsx               # DOM mount point
│   ├── index.css              # Tailwind CSS directives and animations
│   └── vite-env.d.ts          # Vite client types
├── .env.example
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VITE_API_URL` | `http://localhost:8000` | Base URL of the backend FastAPI service |

---

## Getting Started

### 1. Prerequisites
- Node.js 18+ or 20+
- npm, yarn, or pnpm
- Backend API running on `http://localhost:8000`

### 2. Install dependencies
```bash
cd frontend
npm install
```

### 3. Configure environment
```bash
cp .env.example .env
```

### 4. Run development server
```bash
npm run dev
```

The frontend application will be live at:
👉 **[http://localhost:5173](http://localhost:5173)**

### 5. Production build
```bash
npm run build
```
Build output is generated in `frontend/dist/` with zero TypeScript or lint errors.
