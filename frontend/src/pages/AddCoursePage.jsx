import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../utils/store'
import { coursesAPI, categoriesAPI } from '../services/api'
import toast from 'react-hot-toast'

function AddCoursePage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    short_description: '',
    official_url: '',
    category_id: '',
    format: 'online',
    price_type: 'free',
    price_amount: '',
    language: 'ru',
    has_certificate: false,
  })

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    fetchCategories()
  }, [isAuthenticated, navigate])

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll()
      setCategories(response.data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setFormData({ ...formData, [e.target.name]: value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const data = {
        ...formData,
        category_id: parseInt(formData.category_id),
        price_amount: formData.price_amount ? parseFloat(formData.price_amount) : null,
      }

      await coursesAPI.create(data)
      toast.success('Курс добавлен и отправлен на модерацию!')
      navigate('/courses')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка при добавлении курса')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Добавить курс</h1>

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Название курса *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              className="input"
              placeholder="Например: Python для начинающих"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Краткое описание *</label>
            <textarea
              name="short_description"
              value={formData.short_description}
              onChange={handleChange}
              required
              maxLength={300}
              rows={3}
              className="input"
              placeholder="Опишите курс в 2-3 предложениях (до 300 символов)"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Ссылка на курс *</label>
            <input
              type="url"
              name="official_url"
              value={formData.official_url}
              onChange={handleChange}
              required
              className="input"
              placeholder="https://example.com/course"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Категория *</label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                required
                className="input"
              >
                <option value="">Выберите категорию</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Формат *</label>
              <select
                name="format"
                value={formData.format}
                onChange={handleChange}
                className="input"
              >
                <option value="online">Онлайн</option>
                <option value="offline">Офлайн</option>
                <option value="hybrid">Гибридный</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2">Тип цены *</label>
              <select
                name="price_type"
                value={formData.price_type}
                onChange={handleChange}
                className="input"
              >
                <option value="free">Бесплатно</option>
                <option value="one_time">Разовая оплата</option>
                <option value="subscription">Подписка</option>
              </select>
            </div>

            {formData.price_type !== 'free' && (
              <div>
                <label className="block text-sm font-medium mb-2">Цена</label>
                <input
                  type="number"
                  name="price_amount"
                  value={formData.price_amount}
                  onChange={handleChange}
                  className="input"
                  placeholder="Введите сумму"
                />
              </div>
            )}
          </div>

          <div className="mb-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                name="has_certificate"
                checked={formData.has_certificate}
                onChange={handleChange}
                className="w-4 h-4 text-primary-600"
              />
              <span className="text-sm font-medium">Выдается сертификат</span>
            </label>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              <strong>Обратите внимание:</strong> После отправки ваш курс будет проверен модератором.
              Обычно это занимает 1-2 дня.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Отправка...' : 'Добавить курс'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AddCoursePage
