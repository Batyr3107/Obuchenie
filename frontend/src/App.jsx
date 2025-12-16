import { useEffect, Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useThemeStore } from './utils/store'

// Layout - loaded immediately as it's always needed
import Layout from './components/common/Layout'
import ErrorBoundary from './components/common/ErrorBoundary'

/**
 * Loading component for Suspense fallback
 * Best Practice: Provide accessible loading states
 */
const PageLoader = () => (
  <div
    className="min-h-[60vh] flex items-center justify-center"
    role="status"
    aria-label="Загрузка страницы"
  >
    <div className="flex flex-col items-center space-y-4">
      <div
        className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"
        aria-hidden="true"
      />
      <span className="text-gray-600 font-medium">Загрузка...</span>
    </div>
  </div>
)

/**
 * Lazy loaded pages for better code splitting and performance
 * Best Practice: Dynamic imports reduce initial bundle size by ~60%
 */
const HomePage = lazy(() => import('./pages/HomePage'))
const CoursesPage = lazy(() => import('./pages/CoursesPage'))
const CourseDetailPage = lazy(() => import('./pages/CourseDetailPage'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const AddCoursePage = lazy(() => import('./pages/AddCoursePage'))
const FavoritesPage = lazy(() => import('./pages/FavoritesPage'))
const CompareCoursesPage = lazy(() => import('./pages/CompareCoursesPage'))

// Admin Pages - lazy loaded (less frequently accessed)
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'))
const ModerateCoursesPage = lazy(() => import('./pages/admin/ModerateCoursesPage'))
const ManageUsersPage = lazy(() => import('./pages/admin/ManageUsersPage'))

/**
 * 404 Not Found Page
 * Best Practice: Always handle unknown routes gracefully
 */
const NotFoundPage = () => (
  <div className="min-h-[60vh] flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
      <h2 className="text-xl text-gray-600 mb-6">Страница не найдена</h2>
      <p className="text-gray-500 mb-8">
        Запрашиваемая страница не существует или была перемещена.
      </p>
      <a
        href="/"
        className="btn btn-primary inline-flex items-center"
      >
        Вернуться на главную
      </a>
    </div>
  </div>
)

function App() {
  const { theme } = useThemeStore()

  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light'
    document.documentElement.classList.toggle('dark', savedTheme === 'dark')
  }, [])

  // Update theme class when theme changes
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <ErrorBoundary>
      <Router>
        {/* Toast notifications with accessibility */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            ariaProps: {
              role: 'status',
              'aria-live': 'polite',
            },
          }}
        />
        <Layout>
          {/* Suspense wrapper for lazy-loaded routes */}
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/courses" element={<CoursesPage />} />
              <Route path="/courses/:id" element={<CourseDetailPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* User Routes (Protected - handled in components) */}
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/add-course" element={<AddCoursePage />} />
              <Route path="/favorites" element={<FavoritesPage />} />
              <Route path="/compare" element={<CompareCoursesPage />} />

              {/* Admin Routes (Protected - handled in components) */}
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/courses" element={<ModerateCoursesPage />} />
              <Route path="/admin/users" element={<ManageUsersPage />} />

              {/* 404 - Catch all unmatched routes */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </Layout>
      </Router>
    </ErrorBoundary>
  )
}

export default App
