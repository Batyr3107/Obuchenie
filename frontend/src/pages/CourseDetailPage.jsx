import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Star, ExternalLink, BookOpen, Clock, DollarSign, Award,
  Users, TrendingUp, Sparkles, MessageCircle, ArrowLeft,
  CheckCircle, Target, Zap
} from 'lucide-react'
import ReviewCard from '../components/reviews/ReviewCard'
import RatingStars from '../components/reviews/RatingStars'
import SkeletonLoader from '../components/common/SkeletonLoader'
import { coursesAPI, reviewsAPI } from '../services/api'
import { useAuthStore } from '../utils/store'
import toast from 'react-hot-toast'

function CourseDetailPage() {
  const { id } = useParams()
  const { isAuthenticated } = useAuthStore()
  const [course, setCourse] = useState(null)
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCourse()
    fetchReviews()
  }, [id])

  const fetchCourse = async () => {
    try {
      const response = await coursesAPI.getById(id)
      setCourse(response.data)
    } catch (error) {
      toast.error('Ошибка при загрузке курса')
      console.error('Error fetching course:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchReviews = async () => {
    try {
      const response = await reviewsAPI.getAll({ course_id: id })
      setReviews(response.data)
    } catch (error) {
      console.error('Error fetching reviews:', error)
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
        <SkeletonLoader type="detail" count={1} />
      </div>
    )
  }

  if (!course) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center animate-fade-in">
        <div className="card-glass text-center py-16 max-w-md">
          <div className="w-20 h-20 bg-gradient-ocean rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="text-white" size={40} />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Курс не найден</h2>
          <p className="text-gray-600 mb-6">Возможно, курс был удален или URL неверный</p>
          <Link to="/courses" className="btn btn-primary inline-flex items-center">
            <ArrowLeft size={18} className="mr-2" />
            Вернуться к каталогу
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Back Button */}
      <Link
        to="/courses"
        className="inline-flex items-center text-gray-600 hover:text-primary-600 transition-colors font-medium group"
      >
        <ArrowLeft size={18} className="mr-2 group-hover:-translate-x-1 transition-transform" />
        Назад к каталогу
      </Link>

      {/* Course Hero */}
      <div className="relative overflow-hidden bg-gradient-ocean rounded-3xl shadow-2xl animate-fade-in-up">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative grid md:grid-cols-3 gap-8 p-10">
          {/* Logo */}
          {course.logo_url ? (
            <div className="md:col-span-1">
              <div className="relative group overflow-hidden rounded-2xl shadow-2xl">
                <img
                  src={course.logo_url}
                  alt={course.title}
                  className="w-full h-80 object-cover transform group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </div>
          ) : (
            <div className="md:col-span-1">
              <div className="w-full h-80 bg-white/20 backdrop-blur-lg rounded-2xl flex items-center justify-center">
                <TrendingUp className="text-white/40" size={80} />
              </div>
            </div>
          )}

          {/* Info */}
          <div className={course.logo_url ? 'md:col-span-2' : 'md:col-span-3'}>
            <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4">
              <Sparkles size={16} className="text-yellow-300 mr-2" />
              <span className="text-white text-sm font-semibold">{course.format}</span>
            </div>

            <h1 className="text-5xl font-bold text-white mb-4 leading-tight">{course.title}</h1>
            <p className="text-xl text-white/90 mb-6">{course.short_description}</p>

            {/* Rating */}
            <div className="flex items-center space-x-6 mb-8">
              <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-xl">
                <Star className="text-yellow-300" fill="currentColor" size={28} />
                <span className="text-3xl font-bold text-white">{course.avg_rating.toFixed(1)}</span>
              </div>
              <div className="flex items-center space-x-2 text-white/90">
                <Users size={20} />
                <span className="text-lg">{course.total_reviews} отзывов</span>
              </div>
            </div>

            {/* Quick Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center space-x-2 text-white/80 mb-1">
                  <DollarSign size={18} />
                  <span className="text-xs font-medium">Цена</span>
                </div>
                <p className="text-white font-bold">
                  {course.price_type === 'free' ? 'Бесплатно' : `${course.price_amount} ${course.currency}`}
                </p>
              </div>

              {course.duration_weeks && (
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <div className="flex items-center space-x-2 text-white/80 mb-1">
                    <Clock size={18} />
                    <span className="text-xs font-medium">Длительность</span>
                  </div>
                  <p className="text-white font-bold">{course.duration_weeks} недель</p>
                </div>
              )}

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="flex items-center space-x-2 text-white/80 mb-1">
                  <BookOpen size={18} />
                  <span className="text-xs font-medium">Формат</span>
                </div>
                <p className="text-white font-bold">{course.format}</p>
              </div>

              {course.has_certificate && (
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <div className="flex items-center space-x-2 text-white/80 mb-1">
                    <Award size={18} />
                    <span className="text-xs font-medium">Бонус</span>
                  </div>
                  <p className="text-white font-bold flex items-center">
                    <CheckCircle size={16} className="mr-1" />
                    Сертификат
                  </p>
                </div>
              )}
            </div>

            {/* CTA */}
            <a
              href={course.official_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn bg-white text-primary-600 hover:bg-gray-50 shadow-2xl inline-flex items-center space-x-2 text-lg px-8 py-4"
            >
              <Zap size={22} />
              <span>Перейти на сайт курса</span>
              <ExternalLink size={20} />
            </a>
          </div>
        </div>
      </div>

      {/* Detailed Ratings */}
      <div className="card-glass animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="text-3xl font-bold gradient-text mb-6 flex items-center">
          <Target size={28} className="mr-3 text-primary-600" />
          Детальные оценки
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          {[
            { label: 'Качество материала', value: course.avg_content_quality },
            { label: 'Преподаватели', value: course.avg_instructors },
            { label: 'Поддержка', value: course.avg_support },
            { label: 'Цена/Качество', value: course.avg_price_quality },
            { label: 'Практика', value: course.avg_practical },
          ].map((item, index) => (
            <div
              key={index}
              className="text-center p-4 bg-white/50 rounded-xl hover:bg-white/70 transition-all duration-300 hover:-translate-y-1"
            >
              <p className="text-sm text-gray-600 mb-3 font-medium">{item.label}</p>
              <RatingStars rating={item.value} />
              <p className="text-2xl font-bold gradient-text mt-2">{item.value.toFixed(1)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Reviews Section */}
      <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold gradient-text flex items-center">
            <MessageCircle size={28} className="mr-3 text-primary-600" />
            Отзывы студентов
            <span className="ml-3 text-gray-500 text-xl">({reviews.length})</span>
          </h2>
          {isAuthenticated && (
            <Link to={`/courses/${id}/add-review`} className="btn btn-primary inline-flex items-center">
              <Sparkles size={18} className="mr-2" />
              Написать отзыв
            </Link>
          )}
        </div>

        {reviews.length > 0 ? (
          <div className="space-y-6">
            {reviews.map((review, index) => (
              <div
                key={review.id}
                className="animate-fade-in-up"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <ReviewCard review={review} />
              </div>
            ))}
          </div>
        ) : (
          <div className="card-glass text-center py-16 animate-scale-in">
            <div className="w-24 h-24 bg-gradient-fire rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageCircle className="text-white" size={48} />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Отзывов пока нет</h3>
            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Станьте первым, кто поделится своим опытом обучения на этом курсе
            </p>
            {isAuthenticated ? (
              <Link to={`/courses/${id}/add-review`} className="btn btn-primary inline-flex items-center">
                <Sparkles size={18} className="mr-2" />
                Написать первый отзыв
              </Link>
            ) : (
              <Link to="/login" className="btn btn-primary inline-flex items-center">
                <ExternalLink size={18} className="mr-2" />
                Войдите, чтобы оставить отзыв
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default CourseDetailPage
