import { Link } from 'react-router-dom'
import { Search, User, LogOut, Plus, Heart, Shield, Sparkles, Moon, Sun } from 'lucide-react'
import { useAuthStore, useThemeStore } from '../../utils/store'

function Header() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { theme, toggleTheme } = useThemeStore()

  return (
    <header className="bg-white/70 backdrop-blur-xl shadow-glass sticky top-0 z-50 border-b border-white/20 animate-fade-in-down dark:bg-slate-900/70 dark:border-slate-700/30">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-ocean rounded-xl shadow-lg group-hover:shadow-glow transition-all duration-300 flex items-center justify-center group-hover:rotate-6 transform">
              <Sparkles className="text-white" size={20} />
            </div>
            <span className="text-2xl font-bold gradient-text">CourseRate</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link
              to="/courses"
              className="text-gray-700 hover:text-primary-600 font-medium transition-all duration-300 hover:scale-105 relative group dark:text-slate-300 dark:hover:text-primary-400"
            >
              Все курсы
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-ocean group-hover:w-full transition-all duration-300"></span>
            </Link>
            {isAuthenticated && (
              <>
                <Link
                  to="/favorites"
                  className="flex items-center space-x-2 text-gray-700 hover:text-pink-600 font-medium transition-all duration-300 hover:scale-105 relative group dark:text-slate-300 dark:hover:text-pink-400"
                >
                  <Heart size={18} className="group-hover:fill-pink-600 transition-all" />
                  <span>Избранное</span>
                </Link>
                <Link
                  to="/add-course"
                  className="flex items-center space-x-2 px-4 py-2 bg-white/50 rounded-xl text-gray-700 hover:bg-white hover:text-primary-600 font-medium transition-all duration-300 hover:shadow-lg border border-gray-200/50 dark:bg-slate-800/50 dark:text-slate-300 dark:border-slate-700/50 dark:hover:bg-slate-800"
                >
                  <Plus size={18} />
                  <span>Добавить курс</span>
                </Link>
              </>
            )}
            {user?.role === 'admin' && (
              <Link
                to="/admin"
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/50 hover:scale-105"
              >
                <Shield size={18} />
                <span>Админ</span>
              </Link>
            )}
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 bg-white/50 rounded-xl hover:bg-white transition-all duration-300 hover:shadow-lg border border-gray-200/50 hover:scale-110 dark:bg-slate-800/50 dark:border-slate-700/50 dark:hover:bg-slate-800"
              title={theme === 'light' ? 'Темная тема' : 'Светлая тема'}
            >
              {theme === 'light' ? (
                <Moon size={20} className="text-gray-700 dark:text-slate-300" />
              ) : (
                <Sun size={20} className="text-yellow-500 dark:text-yellow-400" />
              )}
            </button>

            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 px-4 py-2 bg-white/50 rounded-xl text-gray-700 hover:bg-white hover:text-primary-600 transition-all duration-300 hover:shadow-lg border border-gray-200/50 dark:bg-slate-800/50 dark:text-slate-300 dark:border-slate-700/50 dark:hover:bg-slate-800"
                >
                  <div className="w-8 h-8 bg-gradient-ocean rounded-full flex items-center justify-center">
                    <User size={16} className="text-white" />
                  </div>
                  <span className="hidden lg:inline font-medium">{user?.email?.split('@')[0]}</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-2 text-gray-500 hover:text-red-600 transition-all duration-300 hover:scale-110 dark:text-slate-400 dark:hover:text-red-500"
                  title="Выйти"
                >
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/login" className="btn btn-secondary px-5 py-2 text-sm">
                  Войти
                </Link>
                <Link to="/register" className="btn btn-primary px-5 py-2 text-sm">
                  Регистрация
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
