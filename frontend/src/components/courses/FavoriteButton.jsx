import { useState, useEffect } from 'react'
import { Heart } from 'lucide-react'
import { useAuthStore } from '../../utils/store'
import api from '../../services/api'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

function FavoriteButton({ courseId, size = 24 }) {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [isFavorite, setIsFavorite] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      checkFavorite()
    }
  }, [courseId, isAuthenticated])

  const checkFavorite = async () => {
    try {
      const response = await api.get(`/favorites/check/${courseId}`)
      setIsFavorite(response.data.is_favorite)
    } catch (error) {
      // Ignore error
    }
  }

  const handleToggle = async (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (!isAuthenticated) {
      toast.error('Войдите, чтобы добавить в избранное')
      navigate('/login')
      return
    }

    setLoading(true)

    try {
      if (isFavorite) {
        await api.delete(`/favorites/${courseId}`)
        setIsFavorite(false)
        toast.success('Удалено из избранного')
      } else {
        await api.post(`/favorites/${courseId}`)
        setIsFavorite(true)
        toast.success('Добавлено в избранное')
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`p-2 rounded-full transition ${
        isFavorite
          ? 'bg-red-100 text-red-600 hover:bg-red-200'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
      title={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
    >
      <Heart
        size={size}
        fill={isFavorite ? 'currentColor' : 'none'}
      />
    </button>
  )
}

export default FavoriteButton
