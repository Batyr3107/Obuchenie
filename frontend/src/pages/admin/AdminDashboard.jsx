import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../../utils/store'
import {
  BarChart, Users, BookOpen, MessageSquare, AlertTriangle,
  Shield, Crown, TrendingUp, Activity, ArrowRight, Loader2
} from 'lucide-react'
import api from '../../services/api'
import toast from 'react-hot-toast'

function AdminDashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/')
      return
    }
    fetchStats()
  }, [user, navigate])

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/stats')
      setStats(response.data)
    } catch (error) {
      toast.error('Ошибка загрузки статистики')
    } finally {
      setLoading(false)
    }
  }

  if (loading || !stats) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="card-glass animate-pulse">
          <div className="h-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card-glass animate-pulse">
              <div className="h-24 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Admin Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl py-16 px-8 shadow-xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-yellow-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative flex items-center justify-between">
          <div>
            <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4 animate-float">
              <Crown size={18} className="text-white mr-2" />
              <span className="text-white font-semibold">Админ панель</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Панель управления
            </h1>
            <p className="text-xl text-white/90">
              Добро пожаловать, {user?.full_name || user?.email}
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-32 h-32 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center animate-float">
              <Shield className="text-white" size={64} />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <StatCard
          title="Пользователи"
          value={stats.users.total}
          subtitle={`${stats.users.blocked} заблокировано`}
          icon={<Users size={32} />}
          gradient="from-blue-500 to-cyan-500"
          change="+12%"
        />

        <StatCard
          title="Курсы"
          value={stats.courses.approved}
          subtitle={`${stats.courses.pending} на модерации`}
          icon={<BookOpen size={32} />}
          gradient="from-green-500 to-emerald-500"
          change="+8%"
        />

        <StatCard
          title="Отзывы"
          value={stats.reviews.total}
          subtitle={`${stats.reviews.blocked} заблокировано`}
          icon={<MessageSquare size={32} />}
          gradient="from-purple-500 to-pink-500"
          change="+15%"
        />

        <StatCard
          title="Жалобы"
          value={stats.reports.pending}
          subtitle="требуют проверки"
          icon={<AlertTriangle size={32} />}
          gradient="from-red-500 to-orange-500"
          change="-5%"
          isNegative={stats.reports.pending > 0}
        />
      </div>

      {/* Quick Actions */}
      <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <h2 className="text-3xl font-bold gradient-text mb-6 flex items-center">
          <Activity size={32} className="mr-3 text-primary-600" />
          Быстрые действия
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ActionCard
            title="Модерация курсов"
            description={`${stats.courses.pending} курсов ожидают проверки`}
            link="/admin/courses"
            gradient="from-blue-500 to-purple-500"
            icon={<BookOpen size={28} />}
            urgent={stats.courses.pending > 0}
          />

          <ActionCard
            title="Управление пользователями"
            description={`${stats.users.total} пользователей в системе`}
            link="/admin/users"
            gradient="from-green-500 to-teal-500"
            icon={<Users size={28} />}
          />

          <ActionCard
            title="Проверка жалоб"
            description={`${stats.reports.pending} жалоб на рассмотрении`}
            link="/admin/reports"
            gradient="from-red-500 to-pink-500"
            icon={<AlertTriangle size={28} />}
            urgent={stats.reports.pending > 5}
          />
        </div>
      </div>

      {/* System Info */}
      <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
        <h3 className="text-2xl font-bold gradient-text mb-6 flex items-center">
          <BarChart size={24} className="mr-3 text-primary-600" />
          Информация о системе
        </h3>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-white/50 dark:bg-slate-800/50 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-slate-400 mb-2">Всего курсов</p>
            <p className="text-3xl font-bold gradient-text">
              {stats.courses.approved + stats.courses.pending}
            </p>
          </div>
          <div className="text-center p-4 bg-white/50 dark:bg-slate-800/50 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-slate-400 mb-2">Активных пользователей</p>
            <p className="text-3xl font-bold gradient-text">
              {stats.users.total - stats.users.blocked}
            </p>
          </div>
          <div className="text-center p-4 bg-white/50 dark:bg-slate-800/50 rounded-xl">
            <p className="text-sm text-gray-600 dark:text-slate-400 mb-2">Публичных отзывов</p>
            <p className="text-3xl font-bold gradient-text">
              {stats.reviews.total - stats.reviews.blocked}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, subtitle, icon, gradient, change, isNegative }) {
  return (
    <div className="card-glass group hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-gray-600 dark:text-slate-400 text-sm font-medium mb-2">{title}</p>
          <p className="text-4xl font-bold text-gray-900 dark:text-slate-100">{value}</p>
        </div>
        <div className={`w-16 h-16 bg-gradient-to-br ${gradient} rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
          <div className="text-white">{icon}</div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-slate-400">{subtitle}</p>
        {change && (
          <span className={`flex items-center text-xs font-semibold ${isNegative ? 'text-red-600' : 'text-green-600'}`}>
            <TrendingUp size={14} className={`mr-1 ${isNegative ? 'rotate-180' : ''}`} />
            {change}
          </span>
        )}
      </div>
    </div>
  )
}

function ActionCard({ title, description, link, gradient, icon, urgent }) {
  return (
    <Link
      to={link}
      className={`relative overflow-hidden bg-gradient-to-br ${gradient} text-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 group`}
    >
      {urgent && (
        <div className="absolute top-4 right-4">
          <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-white opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
          {icon}
        </div>
        <ArrowRight size={24} className="group-hover:translate-x-1 transition-transform" />
      </div>

      <h3 className="text-2xl font-bold mb-2">{title}</h3>
      <p className="text-white/90 text-sm">{description}</p>

      <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
    </Link>
  )
}

export default AdminDashboard
