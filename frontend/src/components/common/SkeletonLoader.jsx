function SkeletonLoader({ type = 'card', count = 1 }) {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className="card animate-pulse">
            {/* Image skeleton */}
            <div className="w-full h-52 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-xl mb-4 animate-gradient bg-[length:200%_100%]"></div>

            {/* Title skeleton */}
            <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg mb-3 w-3/4 animate-gradient bg-[length:200%_100%]"></div>

            {/* Description skeleton */}
            <div className="space-y-2 mb-4">
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-5/6 animate-gradient bg-[length:200%_100%]"></div>
            </div>

            {/* Stats skeleton */}
            <div className="flex items-center justify-between mb-4">
              <div className="h-8 w-20 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-8 w-16 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
            </div>

            {/* Price skeleton */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200">
              <div className="h-8 w-24 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-8 w-28 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-gradient bg-[length:200%_100%]"></div>
            </div>
          </div>
        )

      case 'detail':
        return (
          <div className="animate-pulse space-y-8">
            {/* Header */}
            <div className="card-glass">
              <div className="h-96 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-2xl mb-6 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-10 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg mb-4 w-3/4 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded mb-6 animate-gradient bg-[length:200%_100%]"></div>

              <div className="flex gap-4">
                <div className="h-12 w-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-xl animate-gradient bg-[length:200%_100%]"></div>
                <div className="h-12 w-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-xl animate-gradient bg-[length:200%_100%]"></div>
              </div>
            </div>

            {/* Content */}
            <div className="card-glass space-y-4">
              <div className="h-8 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-1/4 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-5/6 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-4/5 animate-gradient bg-[length:200%_100%]"></div>
            </div>
          </div>
        )

      case 'list':
        return (
          <div className="card-glass flex gap-6 animate-pulse">
            <div className="w-48 h-32 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-xl flex-shrink-0 animate-gradient bg-[length:200%_100%]"></div>
            <div className="flex-1 space-y-4">
              <div className="h-6 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-3/4 animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-gradient bg-[length:200%_100%]"></div>
              <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded w-2/3 animate-gradient bg-[length:200%_100%]"></div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index}>{renderSkeleton()}</div>
      ))}
    </>
  )
}

export default SkeletonLoader
