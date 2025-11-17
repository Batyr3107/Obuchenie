import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { UserPlus, Mail, Lock, User as UserIcon, Sparkles, Loader2, Check } from 'lucide-react'
import { useAuthStore } from '../utils/store'
import toast from 'react-hot-toast'

function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuthStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
  })
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    const result = await register(formData)

    if (result.success) {
      toast.success('Регистрация успешна! Теперь войдите в систему.')
      navigate('/login')
    } else {
      toast.error(result.error || 'Ошибка регистрации')
    }

    setLoading(false)
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 animate-fade-in">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in-down">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-fire rounded-2xl shadow-lg mb-4 animate-float">
            <UserPlus className="text-white" size={32} />
          </div>
          <h1 className="text-4xl font-bold gradient-text-fire mb-2">Начните сейчас!</h1>
          <p className="text-gray-600">Создайте аккаунт за 30 секунд</p>
        </div>

        {/* Form Card */}
        <div className="card-glass animate-fade-in-up">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Full Name Input */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Полное имя
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors">
                  <UserIcon size={20} />
                </div>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="input pl-12"
                  placeholder="Иван Иванов"
                />
              </div>
            </div>

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
                  minLength={8}
                  className="input pl-12"
                  placeholder="Минимум 8 символов"
                />
              </div>
              {formData.password.length > 0 && (
                <div className="mt-2 space-y-1">
                  <div className={`flex items-center text-xs ${formData.password.length >= 8 ? 'text-green-600' : 'text-gray-500'}`}>
                    <Check size={14} className="mr-1" />
                    <span>Минимум 8 символов</span>
                  </div>
                </div>
              )}
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
                  <span>Создание аккаунта...</span>
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  <span>Создать аккаунт</span>
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

          {/* Login Link */}
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Уже есть аккаунт?
            </p>
            <Link
              to="/login"
              className="btn bg-white/50 hover:bg-white text-primary-600 border border-primary-200 w-full flex items-center justify-center space-x-2"
            >
              <UserIcon size={18} />
              <span>Войти в аккаунт</span>
            </Link>
          </div>
        </div>

        {/* Terms Note */}
        <p className="text-center text-xs text-gray-500 mt-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          Регистрируясь, вы соглашаетесь с нашими <br />
          <Link to="/terms" className="text-primary-600 hover:underline">Условиями использования</Link> и{' '}
          <Link to="/privacy" className="text-primary-600 hover:underline">Политикой конфиденциальности</Link>
        </p>
      </div>
    </div>
  )
}

export default RegisterPage
