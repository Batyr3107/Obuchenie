import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import {
  X, ExternalLink, Star, DollarSign, Clock, Award, Globe, Monitor,
  TrendingUp, Check, BookOpen, Sparkles, ArrowRight
} from 'lucide-react'
import api from '../services/api'
import SkeletonLoader from '../components/common/SkeletonLoader'
import toast from 'react-hot-toast'

function CompareCoursesPage() {
  const [searchParams] = useSearchParams()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const ids = searchParams.get('ids')
    if (ids) {
      fetchCourses(ids)
    } else {
      setLoading(false)
    }
  }, [searchParams])

  const fetchCourses = async (ids) => {
    try {
      const response = await api.get('/compare', {
        params: { course_ids: ids }
      })
      setCourses(response.data)
    } catch (error) {
      toast.error('Ошибка загрузки курсов')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = (courseId) => {
    const newCourses = courses.filter(c => c.id !== courseId)
    setCourses(newCourses)

    if (newCourses.length < 2) {
      toast.error('Необходимо минимум 2 курса для сравнения')
    }
  }

  if (loading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="card-glass animate-pulse">
          <div className="h-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <SkeletonLoader type="detail" count={2} />
        </div>
      </div>
    )
  }

  if (courses.length === 0) {
    return (
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="relative overflow-hidden bg-gradient-sunset rounded-3xl py-16 px-8 shadow-xl animate-fade-in-up">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"></div>
          <div className="absolute bottom-0 left-0 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

          <div className="relative">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Сравнение курсов
            </h1>
            <p className="text-xl text-white/90">
              Сравните характеристики курсов и выберите лучший
            </p>
          </div>
        </div>

        {/* Empty State */}
        <div className="card-glass text-center py-20 animate-scale-in">
          <div className="relative inline-block mb-8">
            <div className="absolute inset-0 bg-gradient-ocean opacity-20 rounded-full blur-2xl animate-float"></div>
            <div className="relative w-32 h-32 bg-gradient-ocean rounded-full flex items-center justify-center mx-auto shadow-2xl">
              <TrendingUp className="text-white" size={64} />
            </div>
          </div>

          <h3 className="text-3xl font-bold text-gray-900 dark:text-slate-100 mb-4">
            Нет курсов для сравнения
          </h3>
          <p className="text-gray-600 dark:text-slate-400 mb-8 max-w-md mx-auto text-lg">
            Выберите минимум 2 курса из каталога, чтобы начать сравнение
          </p>

          <Link
            to="/courses"
            className="btn btn-primary inline-flex items-center space-x-2"
          >
            <BookOpen size={20} />
            <span>Перейти к каталогу</span>
            <ArrowRight size={20} />
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="relative overflow-hidden bg-gradient-sunset rounded-3xl py-16 px-8 shadow-xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4 animate-float">
            <TrendingUp size={18} className="text-white mr-2" />
            <span className="text-white font-semibold">Сравнение</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Сравнение курсов
          </h1>
          <p className="text-xl text-white/90">
            Сравниваем {courses.length} {courses.length === 2 ? 'курса' : 'курсов'}
          </p>
        </div>
      </div>

      {/* Course Cards Grid */}
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
        {courses.map((course, index) => (
          <div
            key={course.id}
            className="card-glass animate-fade-in-up group"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            {/* Header with Remove Button */}
            <div className="flex items-start justify-between mb-6">
              <h3 className="text-2xl font-bold gradient-text flex-1 pr-4">{course.title}</h3>
              <button
                onClick={() => handleRemove(course.id)}
                className="p-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-xl hover:bg-red-200 dark:hover:bg-red-900/50 transition-all hover:scale-110"
                title="Удалить из сравнения"
              >
                <X size={20} />
              </button>
            </div>

            {/* Rating */}
            <div className="mb-6 p-4 bg-gradient-ocean rounded-xl text-center">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Star className="text-yellow-300" fill="currentColor" size={28} />
                <span className="text-4xl font-bold text-white">{course.avg_rating.toFixed(1)}</span>
              </div>
              <p className="text-white/90 text-sm">{course.total_reviews} отзывов</p>
            </div>

            {/* Detailed Ratings */}
            <div className="space-y-3 mb-6">
              <RatingBar label="Материал" value={course.avg_content_quality} />
              <RatingBar label="Преподаватели" value={course.avg_instructors} />
              <RatingBar label="Поддержка" value={course.avg_support} />
              <RatingBar label="Цена/Качество" value={course.avg_price_quality} />
              <RatingBar label="Практика" value={course.avg_practical} />
            </div>

            {/* Course Details */}
            <div className="space-y-3 mb-6">
              <DetailRow
                icon={<DollarSign size={18} className="text-green-600" />}
                label="Цена"
                value={course.price_type === 'free' ? 'Бесплатно' : `${course.price_amount} ${course.currency}`}
              />
              <DetailRow
                icon={<Monitor size={18} className="text-blue-600" />}
                label="Формат"
                value={course.format === 'online' ? 'Онлайн' : course.format === 'offline' ? 'Офлайн' : 'Гибридный'}
              />
              <DetailRow
                icon={<Clock size={18} className="text-purple-600" />}
                label="Длительность"
                value={course.duration_weeks ? `${course.duration_weeks} недель` :
                       course.duration_hours ? `${course.duration_hours} часов` : 'Не указано'}
              />
              <DetailRow
                icon={<Award size={18} className="text-yellow-600" />}
                label="Сертификат"
                value={course.has_certificate ? 'Да' : 'Нет'}
                highlight={course.has_certificate}
              />
              <DetailRow
                icon={<Globe size={18} className="text-indigo-600" />}
                label="Язык"
                value={course.language === 'ru' ? '🇷🇺 Русский' : course.language === 'en' ? '🇬🇧 Английский' : 'Другой'}
              />
            </div>

            {/* CTA Button */}
            <a
              href={course.official_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary w-full flex items-center justify-center space-x-2 group-hover:scale-105 transition-transform"
            >
              <span>Перейти к курсу</span>
              <ExternalLink size={18} />
            </a>
          </div>
        ))}
      </div>

      {/* Comparison Summary */}
      {courses.length >= 2 && (
        <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <h3 className="text-2xl font-bold gradient-text mb-6 flex items-center">
            <Check size={28} className="mr-3 text-green-600" />
            Итоговое сравнение
          </h3>

          <div className="grid md:grid-cols-3 gap-6">
            <SummaryCard
              title="Лучший рейтинг"
              course={getBestCourse(courses, 'avg_rating')}
              gradient="from-yellow-500 to-orange-500"
            />
            <SummaryCard
              title="Лучшее соотношение цены и качества"
              course={getBestCourse(courses, 'avg_price_quality')}
              gradient="from-green-500 to-teal-500"
            />
            <SummaryCard
              title="Лучшая поддержка"
              course={getBestCourse(courses, 'avg_support')}
              gradient="from-blue-500 to-purple-500"
            />
          </div>
        </div>
      )}

      {/* Add More Button */}
      {courses.length < 4 && (
        <div className="text-center animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          <Link
            to="/courses"
            className="btn bg-white/50 dark:bg-slate-800/50 hover:bg-white dark:hover:bg-slate-800 text-primary-600 border border-primary-200 dark:border-slate-700 inline-flex items-center space-x-2"
          >
            <Sparkles size={20} />
            <span>Добавить еще курсы</span>
          </Link>
        </div>
      )}
    </div>
  )
}

function RatingBar({ label, value }) {
  const percentage = (value / 5) * 100

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="text-gray-700 dark:text-slate-300 font-medium">{label}</span>
        <span className="font-bold text-gray-900 dark:text-slate-100">{value.toFixed(1)}</span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-ocean h-full rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  )
}

function DetailRow({ icon, label, value, highlight }) {
  return (
    <div className={`flex items-center justify-between p-3 rounded-xl ${highlight ? 'bg-green-50 dark:bg-green-900/20' : 'bg-white/50 dark:bg-slate-800/50'}`}>
      <div className="flex items-center space-x-2">
        {icon}
        <span className="text-sm text-gray-600 dark:text-slate-400">{label}</span>
      </div>
      <span className={`text-sm font-bold ${highlight ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-slate-100'}`}>
        {value}
      </span>
    </div>
  )
}

function SummaryCard({ title, course, gradient }) {
  if (!course) return null

  return (
    <div className={`relative overflow-hidden bg-gradient-to-br ${gradient} text-white rounded-2xl p-6 shadow-xl`}>
      <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
      <div className="relative">
        <h4 className="text-sm font-semibold mb-2 opacity-90">{title}</h4>
        <p className="text-2xl font-bold mb-2">{course.title}</p>
        <div className="flex items-center space-x-2">
          <Star className="text-yellow-300" fill="currentColor" size={20} />
          <span className="text-xl font-bold">{course.avg_rating.toFixed(1)}</span>
        </div>
      </div>
    </div>
  )
}

function getBestCourse(courses, field) {
  if (!courses || courses.length === 0) return null
  return courses.reduce((best, current) =>
    current[field] > best[field] ? current : best
  )
}

export default CompareCoursesPage
