import { useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, Mail, Lock, Sparkles, Loader2 } from 'lucide-react'
import { useAuthStore } from '../utils/store'
import { fireConfetti } from '../utils/confetti'
import toast from 'react-hot-toast'

/**
 * LoginPage Component
 *
 * Best Practices:
 * - Proper form accessibility with labels and aria attributes
 * - useCallback for memoized event handlers
 * - Proper loading and error states
 * - Focus management for better UX
 */
function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = useCallback((e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (error) setError('')
  }, [error])

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await login(formData.email, formData.password)

      if (result.success) {
        toast.success('Вход выполнен успешно!')
        fireConfetti()
        // Navigate after a brief delay for confetti effect
        setTimeout(() => navigate('/'), 800)
      } else {
        setError(result.error || 'Неверный email или пароль')
        toast.error(result.error || 'Ошибка входа')
        setLoading(false)
      }
    } catch (err) {
      setError('Произошла ошибка. Попробуйте позже.')
      toast.error('Произошла ошибка при входе')
      setLoading(false)
    }
  }, [formData.email, formData.password, login, navigate])

  return (
    <main className="min-h-[80vh] flex items-center justify-center py-12 px-4 animate-fade-in">
      <div className="max-w-md w-full">
        {/* Header */}
        <header className="text-center mb-8 animate-fade-in-down">
          <div
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-ocean rounded-2xl shadow-lg mb-4 animate-float"
            aria-hidden="true"
          >
            <LogIn className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-2">С возвращением!</h1>
          <p className="text-gray-600">Войдите в свой аккаунт</p>
        </header>

        {/* Form Card */}
        <div className="card-glass animate-fade-in-up">
          <form
            onSubmit={handleSubmit}
            className="space-y-6"
            aria-label="Форма входа"
            noValidate
          >
            {/* Error Alert */}
            {error && (
              <div
                role="alert"
                aria-live="polite"
                className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm"
              >
                {error}
              </div>
            )}

            {/* Email Input */}
            <div>
              <label
                htmlFor="login-email"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Email адрес
              </label>
              <div className="relative group">
                <div
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors"
                  aria-hidden="true"
                >
                  <Mail size={20} />
                </div>
                <input
                  id="login-email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  autoComplete="email"
                  aria-required="true"
                  aria-describedby={error ? 'login-error' : undefined}
                  className="input pl-12"
                  placeholder="your@email.com"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label
                htmlFor="login-password"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                Пароль
              </label>
              <div className="relative group">
                <div
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors"
                  aria-hidden="true"
                >
                  <Lock size={20} />
                </div>
                <input
                  id="login-password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  autoComplete="current-password"
                  aria-required="true"
                  className="input pl-12"
                  placeholder="••••••••"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              aria-busy={loading}
              className="btn btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" aria-hidden="true" />
                  <span>Вход...</span>
                </>
              ) : (
                <>
                  <LogIn size={20} aria-hidden="true" />
                  <span>Войти</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8" role="separator">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white/60 text-gray-500">или</span>
            </div>
          </div>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Нет аккаунта?
            </p>
            <Link
              to="/register"
              className="btn bg-white/50 hover:bg-white text-primary-600 border border-primary-200 w-full flex items-center justify-center space-x-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              <Sparkles size={18} aria-hidden="true" />
              <span>Создать аккаунт</span>
            </Link>
          </div>
        </div>

        {/* Security Note */}
        <p
          className="text-center text-sm text-gray-500 mt-6 animate-fade-in-up"
          style={{ animationDelay: '0.2s' }}
        >
          <span role="img" aria-label="замок">🔒</span> Ваши данные защищены шифрованием
        </p>
      </div>
    </main>
  )
}

export default LoginPage
