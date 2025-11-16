import { Star } from 'lucide-react'

function RatingStars({ rating, size = 20, editable = false, onChange }) {
  const handleClick = (star) => {
    if (editable && onChange) {
      onChange(star)
    }
  }

  return (
    <div className="flex items-center space-x-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          size={size}
          className={`${
            star <= rating ? 'text-yellow-500' : 'text-gray-300'
          } ${editable ? 'cursor-pointer hover:text-yellow-400' : ''}`}
          fill={star <= rating ? 'currentColor' : 'none'}
          onClick={() => handleClick(star)}
        />
      ))}
    </div>
  )
}

export default RatingStars
