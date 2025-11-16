import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../utils/store'
import { BarChart, Users, BookOpen, MessageSquare, AlertTriangle } from 'lucide-react'
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
    return <div className="text-center py-12">Загрузка...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Админ панель</h1>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Пользователи"
          value={stats.users.total}
          subtitle={`${stats.users.blocked} заблокировано`}
          icon={<Users size={32} className="text-blue-600" />}
          color="blue"
        />

        <StatCard
          title="Курсы"
          value={stats.courses.approved}
          subtitle={`${stats.courses.pending} на модерации`}
          icon={<BookOpen size={32} className="text-green-600" />}
          color="green"
        />

        <StatCard
          title="Отзывы"
          value={stats.reviews.total}
          subtitle={`${stats.reviews.blocked} заблокировано`}
          icon={<MessageSquare size={32} className="text-purple-600" />}
          color="purple"
        />

        <StatCard
          title="Жалобы"
          value={stats.reports.pending}
          subtitle="требуют проверки"
          icon={<AlertTriangle size={32} className="text-red-600" />}
          color="red"
        />
      </div>

      {/* Быстрые действия */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ActionCard
          title="Модерация курсов"
          description={`${stats.courses.pending} курсов ожидают проверки`}
          link="/admin/courses"
          color="bg-blue-500"
        />

        <ActionCard
          title="Управление пользователями"
          description={`${stats.users.total} пользователей`}
          link="/admin/users"
          color="bg-green-500"
        />

        <ActionCard
          title="Проверка жалоб"
          description={`${stats.reports.pending} жалоб на рассмотрении`}
          link="/admin/reports"
          color="bg-red-500"
        />
      </div>
    </div>
  )
}

function StatCard({ title, value, subtitle, icon, color }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
        </div>
        {icon}
      </div>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  )
}

function ActionCard({ title, description, link, color }) {
  return (
    <a href={link} className={`${color} text-white p-6 rounded-lg hover:opacity-90 transition block`}>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-100">{description}</p>
    </a>
  )
}

export default AdminDashboard
