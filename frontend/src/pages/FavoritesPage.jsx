import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, Trash2 } from 'lucide-react'
import { useAuthStore } from '../utils/store'
import CourseCard from '../components/courses/CourseCard'
import api from '../services/api'
import toast from 'react-hot-toast'

function FavoritesPage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    fetchFavorites()
  }, [isAuthenticated, navigate])

  const fetchFavorites = async () => {
    try {
      const response = await api.get('/favorites')
      setFavorites(response.data)
    } catch (error) {
      toast.error('Ошибка загрузки избранного')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (courseId) => {
    try {
      await api.delete(`/favorites/${courseId}`)
      setFavorites(favorites.filter(c => c.id !== courseId))
      toast.success('Удалено из избранного')
    } catch (error) {
      toast.error('Ошибка')
    }
  }

  if (loading) {
    return <div className="text-center py-12">Загрузка...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold flex items-center space-x-2">
          <Heart className="text-red-500" fill="currentColor" />
          <span>Избранное</span>
        </h1>
        <p className="text-gray-600">{favorites.length} курсов</p>
      </div>

      {favorites.length === 0 ? (
        <div className="card text-center py-12">
          <Heart size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600 mb-4">У вас пока нет избранных курсов</p>
          <button
            onClick={() => navigate('/courses')}
            className="btn btn-primary"
          >
            Найти курсы
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((course) => (
            <div key={course.id} className="relative">
              <CourseCard course={course} />
              <button
                onClick={() => handleRemove(course.id)}
                className="absolute top-4 right-4 bg-white rounded-full p-2 shadow-lg hover:bg-red-50 transition"
                title="Удалить из избранного"
              >
                <Trash2 size={18} className="text-red-600" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default FavoritesPage
