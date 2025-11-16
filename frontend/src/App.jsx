import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

// Layout
import Layout from './components/common/Layout'

// Pages
import HomePage from './pages/HomePage'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import AddCoursePage from './pages/AddCoursePage'
import FavoritesPage from './pages/FavoritesPage'
import CompareCoursesPage from './pages/CompareCoursesPage'

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard'
import ModerateCoursesPage from './pages/admin/ModerateCoursesPage'
import ManageUsersPage from './pages/admin/ManageUsersPage'

function App() {
  return (
    <Router>
      <Toaster position="top-right" />
      <Layout>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:id" element={<CourseDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* User Routes */}
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/add-course" element={<AddCoursePage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/compare" element={<CompareCoursesPage />} />

          {/* Admin Routes */}
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/courses" element={<ModerateCoursesPage />} />
          <Route path="/admin/users" element={<ManageUsersPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
