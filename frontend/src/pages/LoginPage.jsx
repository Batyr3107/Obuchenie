import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { LogIn, Mail, Lock, Sparkles, Loader2 } from 'lucide-react'
import { useAuthStore } from '../utils/store'
import toast from 'react-hot-toast'

function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const result = await login(formData.email, formData.password)

    if (result.success) {
      toast.success('Вход выполнен успешно!')
      navigate('/')
    } else {
      toast.error(result.error || 'Ошибка входа')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 animate-fade-in">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in-down">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-ocean rounded-2xl shadow-lg mb-4 animate-float">
            <LogIn className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-2">С возвращением!</h1>
          <p className="text-gray-600">Войдите в свой аккаунт</p>
        </div>

        {/* Form Card */}
        <div className="card-glass animate-fade-in-up">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email адрес
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors">
                  <Mail size={20} />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="input pl-12"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Пароль
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors">
                  <Lock size={20} />
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="input pl-12"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  <span>Вход...</span>
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  <span>Войти</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
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
              className="btn bg-white/50 hover:bg-white text-primary-600 border border-primary-200 w-full flex items-center justify-center space-x-2"
            >
              <Sparkles size={18} />
              <span>Создать аккаунт</span>
            </Link>
          </div>
        </div>

        {/* Security Note */}
        <p className="text-center text-sm text-gray-500 mt-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          🔒 Ваши данные защищены end-to-end шифрованием
        </p>
      </div>
    </div>
  )
}

export default LoginPage
