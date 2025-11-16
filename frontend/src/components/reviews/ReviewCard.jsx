import { Star, ThumbsUp, ThumbsDown } from 'lucide-react'

function ReviewCard({ review }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const renderStars = (rating) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={16}
            className={star <= rating ? 'text-yellow-500' : 'text-gray-300'}
            fill={star <= rating ? 'currentColor' : 'none'}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="card mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            {renderStars(review.overall_rating)}
            <span className="font-semibold text-gray-900">
              {review.overall_rating.toFixed(1)}
            </span>
          </div>
          <p className="text-sm text-gray-600">
            {formatDate(review.created_at)}
          </p>
        </div>

        {review.recommend && (
          <span className="bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-semibold">
            Рекомендует
          </span>
        )}
      </div>

      {/* Detailed Ratings */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        <div>
          <p className="text-xs text-gray-600 mb-1">Материал</p>
          {renderStars(review.content_quality)}
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Преподаватели</p>
          {renderStars(review.instructors)}
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Поддержка</p>
          {renderStars(review.support)}
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Цена/Качество</p>
          {renderStars(review.price_quality)}
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Практика</p>
          {renderStars(review.practical)}
        </div>
      </div>

      {/* Review Text */}
      <p className="text-gray-700 mb-4">{review.review_text}</p>

      {/* Pros & Cons */}
      {(review.pros?.length > 0 || review.cons?.length > 0) && (
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {review.pros?.length > 0 && (
            <div>
              <h4 className="font-semibold text-green-700 mb-2">Плюсы:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                {review.pros.map((pro, index) => (
                  <li key={index}>{pro}</li>
                ))}
              </ul>
            </div>
          )}

          {review.cons?.length > 0 && (
            <div>
              <h4 className="font-semibold text-red-700 mb-2">Минусы:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                {review.cons.map((con, index) => (
                  <li key={index}>{con}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t">
        <div className="flex items-center space-x-4">
          <button className="flex items-center space-x-1 text-gray-600 hover:text-green-600 transition">
            <ThumbsUp size={18} />
            <span className="text-sm">{review.helpful_count}</span>
          </button>
          <button className="flex items-center space-x-1 text-gray-600 hover:text-red-600 transition">
            <ThumbsDown size={18} />
            <span className="text-sm">{review.not_helpful_count}</span>
          </button>
        </div>

        <span className="text-xs text-gray-500">
          {review.completion_status === 'completed' ? 'Прошел полностью' :
           review.completion_status === 'in_progress' ? 'Прохожу сейчас' :
           'Не закончил'}
        </span>
      </div>
    </div>
  )
}

export default ReviewCard
