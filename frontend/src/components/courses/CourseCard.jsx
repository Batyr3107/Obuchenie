import { Link } from 'react-router-dom'
import { Star, Users, Award, Sparkles, TrendingUp } from 'lucide-react'

function CourseCard({ course, isPremium = false, isTop = false }) {
  const cardClass = isTop ? 'card-top' : isPremium ? 'card-premium' : 'card'

  return (
    <div className={`${cardClass} group animate-fade-in-up`}>
      {/* Premium Badge */}
      {isPremium && !isTop && (
        <div className="absolute top-4 right-4 z-10 animate-float">
          <span className="badge badge-premium shadow-xl">
            <Sparkles size={14} className="mr-1" />
            Премиум
          </span>
        </div>
      )}

      {isTop && (
        <div className="absolute top-4 right-4 z-10 animate-float">
          <div className="bg-white/20 backdrop-blur-sm rounded-full p-2 shadow-glow">
            <Award className="text-white" size={24} />
          </div>
        </div>
      )}

      <Link to={`/courses/${course.id}`} className="block">
        {/* Logo */}
        {course.logo_url ? (
          <div className="relative overflow-hidden rounded-xl mb-4 group-hover:shadow-xl transition-all duration-300">
            <img
              src={course.logo_url}
              alt={course.title}
              className="w-full h-52 object-cover transform group-hover:scale-110 transition-transform duration-500"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </div>
        ) : (
          <div className="w-full h-52 bg-gradient-ocean rounded-xl mb-4 flex items-center justify-center group-hover:shadow-xl transition-all duration-300">
            <TrendingUp className="text-white/40" size={48} />
          </div>
        )}

        {/* Title */}
        <h3 className={`text-xl font-bold mb-3 line-clamp-2 group-hover:text-primary-600 transition-colors duration-300 ${
          isTop ? 'text-white group-hover:text-white' : 'text-gray-900'
        }`}>
          {course.title}
        </h3>

        {/* Description */}
        <p className={`text-sm mb-4 line-clamp-2 ${isTop ? 'text-gray-100' : 'text-gray-600'}`}>
          {course.short_description}
        </p>

        {/* Stats */}
        <div className="flex items-center justify-between mb-4">
          {/* Rating */}
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/50 backdrop-blur-sm rounded-lg">
            <Star
              className={`${isTop ? 'text-yellow-300' : 'text-yellow-500'} transition-transform duration-300 group-hover:scale-110`}
              fill="currentColor"
              size={18}
            />
            <span className={`font-bold text-base ${isTop ? 'text-white' : 'text-gray-900'}`}>
              {course.avg_rating.toFixed(1)}
            </span>
          </div>

          {/* Reviews count */}
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/50 backdrop-blur-sm rounded-lg">
            <Users size={16} className={isTop ? 'text-gray-200' : 'text-gray-500'} />
            <span className={`text-sm font-medium ${isTop ? 'text-gray-200' : 'text-gray-600'}`}>
              {course.total_reviews}
            </span>
          </div>
        </div>

        {/* Price */}
        <div className={`flex items-center justify-between pt-4 border-t ${
          isTop ? 'border-white/20' : 'border-gray-200'
        }`}>
          <div className={`text-2xl font-bold ${isTop ? 'text-white' : 'gradient-text'}`}>
            {course.price_type === 'free' ? (
              'Бесплатно'
            ) : (
              <div className="flex items-baseline">
                <span>{course.price_amount}</span>
                <span className="text-sm ml-1 opacity-70">{course.currency}</span>
                {course.price_type === 'subscription' && (
                  <span className="text-sm ml-1 opacity-70">/мес</span>
                )}
              </div>
            )}
          </div>

          <div className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-300 ${
            isTop
              ? 'bg-white/20 text-white group-hover:bg-white/30'
              : 'bg-primary-100 text-primary-700 group-hover:bg-primary-600 group-hover:text-white'
          }`}>
            Подробнее →
          </div>
        </div>
      </Link>
    </div>
  )
}

export default CourseCard
