import { Link } from 'react-router-dom'
import { Star, Users, Award } from 'lucide-react'

function CourseCard({ course, isPremium = false, isTop = false }) {
  const cardClass = isTop ? 'card-top' : isPremium ? 'card-premium' : 'card'

  return (
    <div className={cardClass}>
      {/* Premium Badge */}
      {isPremium && !isTop && (
        <div className="absolute top-2 right-2">
          <span className="bg-gold-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
            Премиум
          </span>
        </div>
      )}

      {isTop && (
        <div className="absolute top-2 right-2">
          <Award className="text-white" size={24} />
        </div>
      )}

      <Link to={`/courses/${course.id}`} className="block">
        {/* Logo */}
        {course.logo_url && (
          <img
            src={course.logo_url}
            alt={course.title}
            className="w-full h-48 object-cover rounded-lg mb-4"
          />
        )}

        {/* Title */}
        <h3 className={`text-lg font-bold mb-2 ${isTop ? 'text-white' : 'text-gray-900'}`}>
          {course.title}
        </h3>

        {/* Description */}
        <p className={`text-sm mb-4 line-clamp-2 ${isTop ? 'text-gray-100' : 'text-gray-600'}`}>
          {course.short_description}
        </p>

        {/* Stats */}
        <div className="flex items-center justify-between mb-4">
          {/* Rating */}
          <div className="flex items-center space-x-1">
            <Star className={`${isTop ? 'text-yellow-300' : 'text-yellow-500'}`} fill="currentColor" size={18} />
            <span className={`font-semibold ${isTop ? 'text-white' : 'text-gray-900'}`}>
              {course.avg_rating.toFixed(1)}
            </span>
          </div>

          {/* Reviews count */}
          <div className="flex items-center space-x-1">
            <Users size={16} className={isTop ? 'text-gray-200' : 'text-gray-500'} />
            <span className={`text-sm ${isTop ? 'text-gray-200' : 'text-gray-600'}`}>
              {course.total_reviews} отзывов
            </span>
          </div>
        </div>

        {/* Price */}
        <div className={`text-lg font-bold ${isTop ? 'text-white' : 'text-primary-600'}`}>
          {course.price_type === 'free' ? (
            'Бесплатно'
          ) : (
            <>
              {course.price_amount} {course.currency}
              {course.price_type === 'subscription' && <span className="text-sm">/мес</span>}
            </>
          )}
        </div>
      </Link>
    </div>
  )
}

export default CourseCard
