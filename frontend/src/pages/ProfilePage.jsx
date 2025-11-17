import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../utils/store'
import {
  User, Mail, Award, Calendar, Star, MessageCircle,
  TrendingUp, Shield, Sparkles, Crown, Target
} from 'lucide-react'
import SkeletonLoader from '../components/common/SkeletonLoader'

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
      <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
        <div className="card-glass animate-pulse">
          <div className="flex items-center space-x-6 mb-8">
            <div className="w-32 h-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-full animate-gradient bg-[length:200%_100%]"></div>
            <div className="flex-1 space-y-4">
              <div className="h-8 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg w-1/2 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-1/3 animate-gradient bg-[length:200%_100%]"></div>
            </div>
          </div>
        </div>
        <SkeletonLoader type="card" count={2} />
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

  const getLevelIcon = (level) => {
    switch (level) {
      case 'admin':
        return <Crown className="text-yellow-500" size={24} />
      case 'moderator':
        return <Shield className="text-blue-500" size={24} />
      default:
        return <User className="text-primary-600" size={24} />
    }
  }

  const getLevelBadge = (level) => {
    switch (level) {
      case 'admin':
        return 'badge bg-gradient-to-r from-yellow-400 to-orange-500 text-white'
      case 'moderator':
        return 'badge bg-gradient-to-r from-blue-400 to-purple-500 text-white'
      default:
        return 'badge badge-secondary'
    }
  }

  const getLevelName = (level) => {
    switch (level) {
      case 'admin':
        return 'Администратор'
      case 'moderator':
        return 'Модератор'
      default:
        return 'Пользователь'
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Profile Hero */}
      <div className="relative overflow-hidden bg-gradient-ocean rounded-3xl shadow-2xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative p-10">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            {/* Avatar */}
            <div className="relative group">
              <div className="absolute inset-0 bg-white/20 rounded-full blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative w-32 h-32 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border-4 border-white/30 shadow-2xl group-hover:scale-110 transition-transform duration-300">
                {getLevelIcon(user.level)}
              </div>
              <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                <span className={getLevelBadge(user.level) + ' shadow-xl animate-float'}>
                  <Sparkles size={12} className="mr-1" />
                  {getLevelName(user.level)}
                </span>
              </div>
            </div>

            {/* User Info */}
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-3 leading-tight">
                {user.full_name || 'Пользователь'}
              </h1>
              <div className="flex items-center justify-center md:justify-start space-x-2 text-white/90 mb-6">
                <Mail size={18} />
                <span className="text-lg">{user.email}</span>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                  <div className="flex items-center justify-center space-x-2 text-white/80 mb-1">
                    <Star size={16} />
                    <span className="text-xs font-medium">Репутация</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{user.reputation_score}</p>
                </div>

                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                  <div className="flex items-center justify-center space-x-2 text-white/80 mb-1">
                    <TrendingUp size={16} />
                    <span className="text-xs font-medium">Полезных</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{user.helpful_votes}</p>
                </div>

                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center col-span-2 md:col-span-1">
                  <div className="flex items-center justify-center space-x-2 text-white/80 mb-1">
                    <Calendar size={16} />
                    <span className="text-xs font-medium">С нами</span>
                  </div>
                  <p className="text-sm font-bold text-white">{formatDate(user.created_at)}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid md:grid-cols-2 gap-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        {/* Reputation Card */}
        <div className="card-glass group hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold gradient-text flex items-center">
              <Target size={24} className="mr-3 text-primary-600" />
              Репутация
            </h3>
            <div className="w-12 h-12 bg-gradient-ocean rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
              <Star className="text-white" size={24} />
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-gradient-ocean opacity-5 rounded-2xl blur-xl"></div>
            <div className="relative bg-white/50 rounded-2xl p-6 text-center">
              <p className="text-sm text-gray-600 mb-2 font-medium">Текущий балл</p>
              <p className="text-5xl font-bold gradient-text mb-2">{user.reputation_score}</p>
              <div className="flex items-center justify-center space-x-2 text-gray-600 text-sm">
                <TrendingUp size={16} className="text-green-500" />
                <span>Продолжайте писать качественные отзывы!</span>
              </div>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center justify-between p-3 bg-white/30 rounded-xl">
              <span className="text-gray-700 font-medium">За отзывы</span>
              <span className="font-bold text-primary-600">+10 за каждый</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-white/30 rounded-xl">
              <span className="text-gray-700 font-medium">Голоса "Полезно"</span>
              <span className="font-bold text-green-600">+5 за каждый</span>
            </div>
          </div>
        </div>

        {/* Activity Card */}
        <div className="card-glass group hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold gradient-text flex items-center">
              <MessageCircle size={24} className="mr-3 text-primary-600" />
              Активность
            </h3>
            <div className="w-12 h-12 bg-gradient-fire rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
              <TrendingUp className="text-white" size={24} />
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 bg-gradient-fire opacity-5 rounded-2xl blur-xl"></div>
            <div className="relative bg-white/50 rounded-2xl p-6 text-center">
              <p className="text-sm text-gray-600 mb-2 font-medium">Полезных голосов</p>
              <p className="text-5xl font-bold gradient-text mb-2">{user.helpful_votes}</p>
              <div className="flex items-center justify-center space-x-2 text-gray-600 text-sm">
                <Award size={16} className="text-yellow-500" />
                <span>Ваши отзывы помогают другим!</span>
              </div>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="text-center p-4 bg-white/30 rounded-xl">
              <p className="text-2xl font-bold text-primary-600 mb-1">
                {Math.floor(user.reputation_score / 10)}
              </p>
              <p className="text-xs text-gray-600 font-medium">Отзывов</p>
            </div>
            <div className="text-center p-4 bg-white/30 rounded-xl">
              <p className="text-2xl font-bold text-green-600 mb-1">
                {user.helpful_votes}
              </p>
              <p className="text-xs text-gray-600 font-medium">Лайков</p>
            </div>
          </div>
        </div>
      </div>

      {/* Account Details */}
      <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <h3 className="text-2xl font-bold gradient-text mb-6 flex items-center">
          <User size={24} className="mr-3 text-primary-600" />
          Детали аккаунта
        </h3>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="group">
            <div className="flex items-center space-x-3 p-4 bg-white/50 rounded-xl hover:bg-white/70 transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-ocean rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Mail className="text-white" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-600 font-medium mb-1">Email адрес</p>
                <p className="font-bold text-gray-900 break-all">{user.email}</p>
              </div>
            </div>
          </div>

          <div className="group">
            <div className="flex items-center space-x-3 p-4 bg-white/50 rounded-xl hover:bg-white/70 transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-fire rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Award className="text-white" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-600 font-medium mb-1">Уровень доступа</p>
                <p className="font-bold text-gray-900 capitalize">{getLevelName(user.level)}</p>
              </div>
            </div>
          </div>

          <div className="group">
            <div className="flex items-center space-x-3 p-4 bg-white/50 rounded-xl hover:bg-white/70 transition-all duration-300 hover:-translate-y-1">
              <div className="w-12 h-12 bg-gradient-sunset rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <Calendar className="text-white" size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-600 font-medium mb-1">Дата регистрации</p>
                <p className="font-bold text-gray-900">{formatDate(user.created_at)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Achievement Badges (if admin or moderator) */}
      {(user.level === 'admin' || user.level === 'moderator') && (
        <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <h3 className="text-2xl font-bold gradient-text mb-6 flex items-center">
            <Crown size={24} className="mr-3 text-yellow-500" />
            Особые права
          </h3>

          <div className="grid md:grid-cols-2 gap-4">
            {user.level === 'admin' && (
              <>
                <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
                  <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                    <Shield className="text-white" size={20} />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">Полный доступ</p>
                    <p className="text-xs text-gray-600">Управление всей платформой</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl border border-yellow-200">
                  <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                    <Crown className="text-white" size={20} />
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">Администратор</p>
                    <p className="text-xs text-gray-600">Максимальные привилегии</p>
                  </div>
                </div>
              </>
            )}
            {user.level === 'moderator' && (
              <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-500 rounded-lg flex items-center justify-center">
                  <Shield className="text-white" size={20} />
                </div>
                <div>
                  <p className="font-bold text-gray-900">Модератор</p>
                  <p className="text-xs text-gray-600">Управление контентом</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfilePage
