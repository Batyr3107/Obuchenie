import { useState, useEffect, useCallback, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { BookOpen, Filter, X, Sparkles } from 'lucide-react'
import CourseCard from '../components/courses/CourseCard'
import CourseFilters from '../components/courses/CourseFilters'
import SkeletonLoader from '../components/common/SkeletonLoader'
import { coursesAPI } from '../services/api'
import { reportError } from '../utils/errorReporter'
import toast from 'react-hot-toast'

/**
 * CoursesPage Component
 *
 * PERFORMANCE:
 * - Uses individual filter values in useEffect deps to prevent unnecessary re-renders
 * - AbortController for canceling requests on filter change
 * - useCallback for stable handler references
 */
function CoursesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category_id: null,
    min_rating: null,
  })

  // AbortController ref for canceling requests
  const abortControllerRef = useRef(null)

  // PERFORMANCE: Use individual values to prevent object reference issues
  const { search, category_id, min_rating } = filters

  useEffect(() => {
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new controller
    abortControllerRef.current = new AbortController()

    const fetchCourses = async () => {
      try {
        setLoading(true)
        const params = {}

        if (search) params.search = search
        if (category_id) params.category_id = category_id
        if (min_rating) params.min_rating = min_rating

        const response = await coursesAPI.getAll(params)
        setCourses(response.data)
      } catch (error) {
        // Don't show error if request was cancelled
        if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
          return
        }
        toast.error('Ошибка при загрузке курсов')
        reportError(error, { component: 'CoursesPage', action: 'fetchCourses', filters })
      } finally {
        setLoading(false)
      }
    }

    fetchCourses()

    // Cleanup: cancel request on unmount or filter change
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [search, category_id, min_rating]) // PERFORMANCE: Individual values, not object

  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(newFilters)

    // Update URL params
    const params = new URLSearchParams()
    if (newFilters.search) params.set('search', newFilters.search)
    setSearchParams(params)
  }, [setSearchParams])

  const resetFilters = useCallback(() => {
    handleFiltersChange({ search: '', category_id: null, min_rating: null })
  }, [handleFiltersChange])

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="relative overflow-hidden bg-gradient-ocean rounded-3xl py-16 px-8 shadow-xl">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-4">
            <BookOpen size={18} className="text-white mr-2" />
            <span className="text-white font-semibold">Каталог курсов</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Все курсы
          </h1>
          <p className="text-xl text-white/90 max-w-2xl">
            Найдите идеальный курс из {courses.length > 0 ? courses.length : '500+'} программ обучения
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <div className="card-glass">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <Filter size={20} className="text-primary-600" />
                  <h3 className="font-bold text-lg">Фильтры</h3>
                </div>
                {(filters.search || filters.category_id || filters.min_rating) && (
                  <button
                    onClick={resetFilters}
                    className="text-sm text-gray-600 hover:text-primary-600 transition-colors flex items-center space-x-1"
                  >
                    <X size={16} />
                    <span>Сбросить</span>
                  </button>
                )}
              </div>
              <CourseFilters
                filters={filters}
                onFiltersChange={handleFiltersChange}
              />
            </div>
          </div>
        </div>

        {/* Courses Grid */}
        <div className="lg:col-span-3">
          {/* Results count */}
          {!loading && courses.length > 0 && (
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                Найдено <span className="font-bold text-gray-900">{courses.length}</span> {courses.length === 1 ? 'курс' : 'курсов'}
              </p>
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              <SkeletonLoader type="card" count={6} />
            </div>
          ) : courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {courses.map((course, index) => (
                <div
                  key={course.id}
                  className="animate-fade-in-up"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <CourseCard course={course} />
                </div>
              ))}
            </div>
          ) : (
            <div className="card-glass text-center py-20 animate-scale-in">
              <div className="w-24 h-24 bg-gradient-ocean rounded-full flex items-center justify-center mx-auto mb-6">
                <BookOpen className="text-white" size={48} />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Курсы не найдены</h3>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Попробуйте изменить критерии поиска или сбросить все фильтры
              </p>
              <button
                onClick={resetFilters}
                className="btn btn-primary inline-flex items-center"
              >
                <X size={18} className="mr-2" />
                Сбросить фильтры
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CoursesPage
