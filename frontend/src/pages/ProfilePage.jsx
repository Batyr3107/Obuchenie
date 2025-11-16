import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../utils/store'
import { User, Mail, Award, Calendar } from 'lucide-react'

function ProfilePage() {
  const navigate = useNavigate()
  const { isAuthenticated, user, fetchUser } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    if (!user) {
      fetchUser()
    }
  }, [isAuthenticated, user, navigate, fetchUser])

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Загрузка...</p>
      </div>
    )
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Профиль</h1>

      <div className="card mb-6">
        <div className="flex items-center space-x-4 mb-6">
          <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
            <User size={40} className="text-primary-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">{user.full_name || 'Пользователь'}</h2>
            <p className="text-gray-600">{user.email}</p>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <Mail size={20} className="text-gray-500" />
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-semibold">{user.email}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Award size={20} className="text-gray-500" />
            <div>
              <p className="text-sm text-gray-600">Уровень</p>
              <p className="font-semibold capitalize">{user.level}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Calendar size={20} className="text-gray-500" />
            <div>
              <p className="text-sm text-gray-600">Регистрация</p>
              <p className="font-semibold">{formatDate(user.created_at)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-bold mb-4">Статистика</h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">Репутация</p>
            <p className="text-2xl font-bold text-primary-600">{user.reputation_score}</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">Полезных отзывов</p>
            <p className="text-2xl font-bold text-green-600">{user.helpful_votes}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
