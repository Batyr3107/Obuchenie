import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, Trash2, BookOpen, Sparkles, X } from 'lucide-react'
import { useAuthStore } from '../utils/store'
import CourseCard from '../components/courses/CourseCard'
import SkeletonLoader from '../components/common/SkeletonLoader'
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
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="card-glass animate-pulse">
          <div className="h-16 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg w-1/3 mb-4 animate-gradient bg-[length:200%_100%]"></div>
          <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-1/4 animate-gradient bg-[length:200%_100%]"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SkeletonLoader type="card" count={6} />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="relative overflow-hidden bg-gradient-fire rounded-3xl py-16 px-8 shadow-xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4 animate-float">
            <Heart size={18} className="text-white mr-2" fill="currentColor" />
            <span className="text-white font-semibold">Избранное</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Мои любимые курсы
          </h1>
          <div className="flex items-center space-x-4">
            <p className="text-xl text-white/90">
              {favorites.length === 0
                ? 'Добавьте курсы в избранное, чтобы быстро находить их'
                : `У вас ${favorites.length} ${favorites.length === 1 ? 'курс' : 'курсов'} в избранном`
              }
            </p>
            {favorites.length > 0 && (
              <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-xl">
                <span className="text-3xl font-bold text-white">{favorites.length}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Favorites Grid or Empty State */}
      {favorites.length === 0 ? (
        <div className="card-glass text-center py-20 animate-scale-in">
          <div className="relative inline-block mb-8">
            <div className="absolute inset-0 bg-gradient-fire opacity-20 rounded-full blur-2xl animate-float"></div>
            <div className="relative w-32 h-32 bg-gradient-fire rounded-full flex items-center justify-center mx-auto shadow-2xl">
              <Heart className="text-white" size={64} fill="currentColor" />
            </div>
          </div>

          <h3 className="text-3xl font-bold text-gray-900 mb-4">
            Нет избранных курсов
          </h3>
          <p className="text-gray-600 mb-8 max-w-md mx-auto text-lg">
            Добавляйте понравившиеся курсы в избранное, чтобы всегда иметь к ним быстрый доступ
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={() => navigate('/courses')}
              className="btn btn-primary inline-flex items-center space-x-2"
            >
              <BookOpen size={20} />
              <span>Найти курсы</span>
            </button>
            <button
              onClick={() => navigate('/')}
              className="btn bg-white/50 hover:bg-white text-gray-700 border border-gray-200 inline-flex items-center space-x-2"
            >
              <Sparkles size={20} />
              <span>На главную</span>
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Info Card */}
          <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Отслеживайте свои любимые курсы
                </h3>
                <p className="text-gray-600">
                  Нажмите на иконку корзины, чтобы удалить курс из избранного
                </p>
              </div>
              <div className="hidden md:block w-16 h-16 bg-gradient-fire rounded-2xl flex items-center justify-center shadow-lg">
                <Heart className="text-white" size={32} fill="currentColor" />
              </div>
            </div>
          </div>

          {/* Courses Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {favorites.map((course, index) => (
              <div
                key={course.id}
                className="relative group animate-fade-in-up"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <CourseCard course={course} />

                {/* Remove Button */}
                <button
                  onClick={() => handleRemove(course.id)}
                  className="absolute top-4 right-4 z-20 bg-white/90 backdrop-blur-sm rounded-xl p-3 shadow-lg hover:bg-red-50 hover:shadow-xl transition-all duration-300 opacity-0 group-hover:opacity-100 hover:scale-110 transform"
                  title="Удалить из избранного"
                >
                  <Trash2 size={18} className="text-red-600" />
                </button>

                {/* Favorite Badge */}
                <div className="absolute top-4 left-4 z-10">
                  <span className="badge bg-gradient-to-r from-red-400 to-pink-500 text-white shadow-xl animate-float">
                    <Heart size={12} className="mr-1" fill="currentColor" />
                    Избранное
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Actions */}
          <div className="card-glass text-center animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <p className="text-gray-600 mb-4">
              Хотите найти еще больше интересных курсов?
            </p>
            <button
              onClick={() => navigate('/courses')}
              className="btn btn-primary inline-flex items-center space-x-2"
            >
              <BookOpen size={20} />
              <span>Перейти в каталог курсов</span>
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default FavoritesPage
