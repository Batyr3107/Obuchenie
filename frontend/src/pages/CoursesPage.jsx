import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import CourseCard from '../components/courses/CourseCard'
import CourseFilters from '../components/courses/CourseFilters'
import { coursesAPI } from '../services/api'
import toast from 'react-hot-toast'

function CoursesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category_id: null,
    min_rating: null,
  })

  useEffect(() => {
    fetchCourses()
  }, [filters])

  const fetchCourses = async () => {
    try {
      setLoading(true)
      const params = {}

      if (filters.search) params.search = filters.search
      if (filters.category_id) params.category_id = filters.category_id
      if (filters.min_rating) params.min_rating = filters.min_rating

      const response = await coursesAPI.getAll(params)
      setCourses(response.data)
    } catch (error) {
      toast.error('Ошибка при загрузке курсов')
      console.error('Error fetching courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters)

    // Update URL params
    const params = new URLSearchParams()
    if (newFilters.search) params.set('search', newFilters.search)
    setSearchParams(params)
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Все курсы</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <CourseFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />
        </div>

        {/* Courses Grid */}
        <div className="lg:col-span-3">
          {loading ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Загрузка...</p>
            </div>
          ) : courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {courses.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          ) : (
            <div className="card text-center py-12">
              <p className="text-gray-600 mb-4">Курсы не найдены</p>
              <button
                onClick={() => handleFiltersChange({ search: '', category_id: null, min_rating: null })}
                className="btn btn-secondary"
              >
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
