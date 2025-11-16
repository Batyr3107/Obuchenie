import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Ban, CheckCircle, Shield } from 'lucide-react'
import { useAuthStore } from '../../utils/store'
import api from '../../services/api'
import toast from 'react-hot-toast'

function ManageUsersPage() {
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const [users, setUsers] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!currentUser || currentUser.role !== 'admin') {
      navigate('/')
      return
    }
    fetchUsers()
  }, [currentUser, navigate, search])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users', {
        params: { search: search || undefined }
      })
      setUsers(response.data)
    } catch (error) {
      toast.error('Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  const handleBlock = async (userId) => {
    try {
      await api.post(`/admin/users/${userId}/block`)
      toast.success('Пользователь заблокирован')
      fetchUsers()
    } catch (error) {
      toast.error('Ошибка')
    }
  }

  const handleUnblock = async (userId) => {
    try {
      await api.post(`/admin/users/${userId}/unblock`)
      toast.success('Пользователь разблокирован')
      fetchUsers()
    } catch (error) {
      toast.error('Ошибка')
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ru-RU')
  }

  if (loading) {
    return <div className="text-center py-12">Загрузка...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Управление пользователями</h1>

      {/* Поиск */}
      <div className="card mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Поиск по email или имени..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Таблица пользователей */}
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-3 px-4">Email</th>
              <th className="text-left py-3 px-4">Имя</th>
              <th className="text-left py-3 px-4">Роль</th>
              <th className="text-left py-3 px-4">Статус</th>
              <th className="text-left py-3 px-4">Регистрация</th>
              <th className="text-left py-3 px-4">Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b hover:bg-gray-50">
                <td className="py-3 px-4">{user.email}</td>
                <td className="py-3 px-4">{user.full_name || '-'}</td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {user.role}
                  </span>
                </td>
                <td className="py-3 px-4">
                  {user.is_blocked ? (
                    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                      Заблокирован
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                      Активен
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                <td className="py-3 px-4">
                  {user.role !== 'admin' && (
                    <div className="flex space-x-2">
                      {user.is_blocked ? (
                        <button
                          onClick={() => handleUnblock(user.id)}
                          className="text-green-600 hover:text-green-700"
                          title="Разблокировать"
                        >
                          <CheckCircle size={20} />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleBlock(user.id)}
                          className="text-red-600 hover:text-red-700"
                          title="Заблокировать"
                        >
                          <Ban size={20} />
                        </button>
                      )}
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ManageUsersPage
