import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Plus, BookOpen, Link as LinkIcon, Tag, Monitor, DollarSign,
  Globe, Award, AlertCircle, Loader2, CheckCircle, Sparkles
} from 'lucide-react'
import { useAuthStore } from '../utils/store'
import { coursesAPI, categoriesAPI } from '../services/api'
import { fireStars } from '../utils/confetti'
import toast from 'react-hot-toast'

function AddCoursePage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [categoriesLoading, setCategoriesLoading] = useState(true)
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
      toast.error('Ошибка загрузки категорий')
    } finally {
      setCategoriesLoading(false)
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
      toast.success('🎉 Курс добавлен и отправлен на модерацию!')
      fireStars()
      setTimeout(() => navigate('/courses'), 1000)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Ошибка при добавлении курса')
      setLoading(false)
    }
  }

  const charCount = formData.short_description.length
  const charLimit = 300

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="relative overflow-hidden bg-gradient-ocean rounded-3xl py-16 px-8 shadow-xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4 animate-float">
            <Plus size={18} className="text-white mr-2" />
            <span className="text-white font-semibold">Новый курс</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Добавить курс
          </h1>
          <p className="text-xl text-white/90">
            Поделитесь своим любимым курсом с сообществом
          </p>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid md:grid-cols-3 gap-4 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <div className="card-glass text-center p-6">
          <div className="w-12 h-12 bg-gradient-ocean rounded-xl flex items-center justify-center mx-auto mb-3">
            <CheckCircle className="text-white" size={24} />
          </div>
          <h3 className="font-bold text-gray-900 dark:text-slate-100 mb-1">Модерация</h3>
          <p className="text-sm text-gray-600 dark:text-slate-400">1-2 дня проверки</p>
        </div>
        <div className="card-glass text-center p-6">
          <div className="w-12 h-12 bg-gradient-fire rounded-xl flex items-center justify-center mx-auto mb-3">
            <Sparkles className="text-white" size={24} />
          </div>
          <h3 className="font-bold text-gray-900 dark:text-slate-100 mb-1">Качество</h3>
          <p className="text-sm text-gray-600 dark:text-slate-400">Проверенные курсы</p>
        </div>
        <div className="card-glass text-center p-6">
          <div className="w-12 h-12 bg-gradient-sunset rounded-xl flex items-center justify-center mx-auto mb-3">
            <Award className="text-white" size={24} />
          </div>
          <h3 className="font-bold text-gray-900 dark:text-slate-100 mb-1">Репутация</h3>
          <p className="text-sm text-gray-600 dark:text-slate-400">+10 за добавление</p>
        </div>
      </div>

      {/* Form Card */}
      <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Course Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
              Название курса *
            </label>
            <div className="relative group">
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors">
                <BookOpen size={20} />
              </div>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                className="input pl-12"
                placeholder="Например: Python для начинающих"
              />
            </div>
          </div>

          {/* Short Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
              Краткое описание *
            </label>
            <textarea
              name="short_description"
              value={formData.short_description}
              onChange={handleChange}
              required
              maxLength={charLimit}
              rows={4}
              className="input resize-none"
              placeholder="Опишите курс в 2-3 предложениях (до 300 символов)"
            />
            <div className="flex items-center justify-between mt-2">
              <p className="text-xs text-gray-500 dark:text-slate-400">
                Расскажите, что студенты узнают из этого курса
              </p>
              <span className={`text-xs font-medium ${charCount > charLimit - 50 ? 'text-orange-600' : 'text-gray-500 dark:text-slate-400'}`}>
                {charCount}/{charLimit}
              </span>
            </div>
          </div>

          {/* Official URL */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
              Ссылка на курс *
            </label>
            <div className="relative group">
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors">
                <LinkIcon size={20} />
              </div>
              <input
                type="url"
                name="official_url"
                value={formData.official_url}
                onChange={handleChange}
                required
                className="input pl-12"
                placeholder="https://example.com/course"
              />
            </div>
          </div>

          {/* Category and Format */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
                Категория *
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors z-10 pointer-events-none">
                  <Tag size={20} />
                </div>
                <select
                  name="category_id"
                  value={formData.category_id}
                  onChange={handleChange}
                  required
                  disabled={categoriesLoading}
                  className="input pl-12 appearance-none cursor-pointer"
                >
                  <option value="">
                    {categoriesLoading ? 'Загрузка...' : 'Выберите категорию'}
                  </option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
                Формат *
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors z-10 pointer-events-none">
                  <Monitor size={20} />
                </div>
                <select
                  name="format"
                  value={formData.format}
                  onChange={handleChange}
                  className="input pl-12 appearance-none cursor-pointer"
                >
                  <option value="online">🌐 Онлайн</option>
                  <option value="offline">🏫 Офлайн</option>
                  <option value="hybrid">🔄 Гибридный</option>
                </select>
              </div>
            </div>
          </div>

          {/* Price Type and Amount */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
                Тип цены *
              </label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors z-10 pointer-events-none">
                  <DollarSign size={20} />
                </div>
                <select
                  name="price_type"
                  value={formData.price_type}
                  onChange={handleChange}
                  className="input pl-12 appearance-none cursor-pointer"
                >
                  <option value="free">💚 Бесплатно</option>
                  <option value="one_time">💰 Разовая оплата</option>
                  <option value="subscription">🔄 Подписка</option>
                </select>
              </div>
            </div>

            {formData.price_type !== 'free' && (
              <div className="animate-fade-in">
                <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
                  Цена (₽)
                </label>
                <input
                  type="number"
                  name="price_amount"
                  value={formData.price_amount}
                  onChange={handleChange}
                  className="input"
                  placeholder="Введите сумму"
                  min="0"
                  step="0.01"
                />
              </div>
            )}
          </div>

          {/* Language */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-slate-300 mb-2">
              Язык курса *
            </label>
            <div className="relative group">
              <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-primary-600 transition-colors z-10 pointer-events-none">
                <Globe size={20} />
              </div>
              <select
                name="language"
                value={formData.language}
                onChange={handleChange}
                className="input pl-12 appearance-none cursor-pointer"
              >
                <option value="ru">🇷🇺 Русский</option>
                <option value="en">🇬🇧 Английский</option>
                <option value="other">🌍 Другой</option>
              </select>
            </div>
          </div>

          {/* Certificate Checkbox */}
          <div className="card bg-white/50 dark:bg-slate-800/50 p-5">
            <label className="flex items-start space-x-3 cursor-pointer group">
              <input
                type="checkbox"
                name="has_certificate"
                checked={formData.has_certificate}
                onChange={handleChange}
                className="mt-1 w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500 cursor-pointer"
              />
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <Award size={18} className="text-primary-600" />
                  <span className="font-semibold text-gray-900 dark:text-slate-100">
                    Выдается сертификат
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-slate-400">
                  Отметьте, если после завершения курса студенты получают сертификат
                </p>
              </div>
            </label>
          </div>

          {/* Moderation Notice */}
          <div className="card bg-gradient-to-br from-blue-50 to-purple-50 dark:from-slate-800 dark:to-slate-700 border-2 border-primary-200 dark:border-slate-600">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center flex-shrink-0">
                <AlertCircle className="text-white" size={20} />
              </div>
              <div>
                <h4 className="font-bold text-gray-900 dark:text-slate-100 mb-2">
                  Процесс модерации
                </h4>
                <p className="text-sm text-gray-700 dark:text-slate-300 mb-2">
                  После отправки ваш курс будет проверен модератором на соответствие правилам:
                </p>
                <ul className="text-sm text-gray-600 dark:text-slate-400 space-y-1 ml-4">
                  <li>• Корректность информации</li>
                  <li>• Рабочая ссылка на курс</li>
                  <li>• Соответствие категории</li>
                </ul>
                <p className="text-sm text-primary-700 dark:text-primary-400 font-medium mt-3">
                  ⏱️ Обычно проверка занимает 1-2 рабочих дня
                </p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full flex items-center justify-center space-x-2 text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                <span>Отправка на модерацию...</span>
              </>
            ) : (
              <>
                <Sparkles size={24} />
                <span>Добавить курс</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AddCoursePage
