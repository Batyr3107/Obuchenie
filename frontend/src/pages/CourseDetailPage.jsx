import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Star, ExternalLink, BookOpen, Clock, DollarSign, Award } from 'lucide-react'
import ReviewCard from '../components/reviews/ReviewCard'
import RatingStars from '../components/reviews/RatingStars'
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
      <div className="text-center py-12">
        <p className="text-gray-600">Загрузка...</p>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Курс не найден</p>
        <Link to="/courses" className="btn btn-primary mt-4 inline-block">
          Вернуться к списку
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Course Header */}
      <div className="card mb-6">
        <div className="grid md:grid-cols-3 gap-6">
          {/* Logo */}
          {course.logo_url && (
            <div className="md:col-span-1">
              <img
                src={course.logo_url}
                alt={course.title}
                className="w-full h-64 object-cover rounded-lg"
              />
            </div>
          )}

          {/* Info */}
          <div className={course.logo_url ? 'md:col-span-2' : 'md:col-span-3'}>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{course.title}</h1>
            <p className="text-gray-700 mb-6">{course.short_description}</p>

            {/* Rating */}
            <div className="flex items-center space-x-4 mb-6">
              <div className="flex items-center space-x-2">
                <Star className="text-yellow-500" fill="currentColor" size={24} />
                <span className="text-2xl font-bold">{course.avg_rating.toFixed(1)}</span>
              </div>
              <span className="text-gray-600">({course.total_reviews} отзывов)</span>
            </div>

            {/* Quick Info */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex items-center space-x-2">
                <DollarSign size={20} className="text-gray-500" />
                <span className="text-gray-700">
                  {course.price_type === 'free' ? 'Бесплатно' : `${course.price_amount} ${course.currency}`}
                </span>
              </div>

              {course.duration_weeks && (
                <div className="flex items-center space-x-2">
                  <Clock size={20} className="text-gray-500" />
                  <span className="text-gray-700">{course.duration_weeks} недель</span>
                </div>
              )}

              <div className="flex items-center space-x-2">
                <BookOpen size={20} className="text-gray-500" />
                <span className="text-gray-700">{course.format}</span>
              </div>

              {course.has_certificate && (
                <div className="flex items-center space-x-2">
                  <Award size={20} className="text-gray-500" />
                  <span className="text-gray-700">Сертификат</span>
                </div>
              )}
            </div>

            {/* CTA */}
            <a
              href={course.official_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary inline-flex items-center space-x-2"
            >
              <span>Перейти на сайт курса</span>
              <ExternalLink size={18} />
            </a>
          </div>
        </div>
      </div>

      {/* Detailed Ratings */}
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-4">Детальные оценки</h2>
        <div className="grid md:grid-cols-5 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-2">Качество материала</p>
            <RatingStars rating={course.avg_content_quality} />
            <p className="text-sm font-semibold mt-1">{course.avg_content_quality.toFixed(1)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Преподаватели</p>
            <RatingStars rating={course.avg_instructors} />
            <p className="text-sm font-semibold mt-1">{course.avg_instructors.toFixed(1)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Поддержка</p>
            <RatingStars rating={course.avg_support} />
            <p className="text-sm font-semibold mt-1">{course.avg_support.toFixed(1)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Цена/Качество</p>
            <RatingStars rating={course.avg_price_quality} />
            <p className="text-sm font-semibold mt-1">{course.avg_price_quality.toFixed(1)}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-2">Практика</p>
            <RatingStars rating={course.avg_practical} />
            <p className="text-sm font-semibold mt-1">{course.avg_practical.toFixed(1)}</p>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Отзывы</h2>
          {isAuthenticated && (
            <Link to={`/courses/${id}/add-review`} className="btn btn-primary">
              Написать отзыв
            </Link>
          )}
        </div>

        {reviews.length > 0 ? (
          <div>
            {reviews.map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        ) : (
          <div className="card text-center py-12">
            <p className="text-gray-600 mb-4">Отзывов пока нет</p>
            {isAuthenticated ? (
              <Link to={`/courses/${id}/add-review`} className="btn btn-primary inline-block">
                Написать первый отзыв
              </Link>
            ) : (
              <Link to="/login" className="btn btn-primary inline-block">
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
