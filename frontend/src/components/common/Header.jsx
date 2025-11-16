import { Link } from 'react-router-dom'
import { Search, User, LogOut, Plus, Heart, Shield } from 'lucide-react'
import { useAuthStore } from '../../utils/store'

function Header() {
  const { isAuthenticated, user, logout } = useAuthStore()

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg"></div>
            <span className="text-xl font-bold text-gray-900">CourseRate</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/courses" className="text-gray-700 hover:text-primary-600 transition">
              Все курсы
            </Link>
            {isAuthenticated && (
              <>
                <Link to="/favorites" className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition">
                  <Heart size={18} />
                  <span>Избранное</span>
                </Link>
                <Link to="/add-course" className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition">
                  <Plus size={18} />
                  <span>Добавить курс</span>
                </Link>
              </>
            )}
            {user?.role === 'admin' && (
              <Link to="/admin" className="flex items-center space-x-1 text-purple-600 hover:text-purple-700 transition font-semibold">
                <Shield size={18} />
                <span>Админ</span>
              </Link>
            )}
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile" className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition">
                  <User size={20} />
                  <span className="hidden md:inline">{user?.email}</span>
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center space-x-2 text-gray-700 hover:text-red-600 transition"
                >
                  <LogOut size={20} />
                  <span className="hidden md:inline">Выйти</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn-secondary">
                  Войти
                </Link>
                <Link to="/register" className="btn btn-primary">
                  Регистрация
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
