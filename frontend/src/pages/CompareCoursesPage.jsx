import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { X, ExternalLink, Star } from 'lucide-react'
import api from '../services/api'
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
    return <div className="text-center py-12">Загрузка...</div>
  }

  if (courses.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600 mb-4">Выберите курсы для сравнения</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Сравнение курсов</h1>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="border p-4 bg-gray-50 text-left">Характеристика</th>
              {courses.map((course) => (
                <th key={course.id} className="border p-4 bg-gray-50 min-w-[250px]">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-bold mb-2">{course.title}</h3>
                      <a
                        href={course.official_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 inline-flex items-center space-x-1 text-sm"
                      >
                        <span>Сайт</span>
                        <ExternalLink size={14} />
                      </a>
                    </div>
                    <button
                      onClick={() => handleRemove(course.id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <X size={20} />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Рейтинг */}
            <tr>
              <td className="border p-4 font-semibold">Общий рейтинг</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center">
                  <div className="flex items-center justify-center space-x-2">
                    <Star className="text-yellow-500" fill="currentColor" size={20} />
                    <span className="text-xl font-bold">{course.avg_rating.toFixed(1)}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {course.total_reviews} отзывов
                  </p>
                </td>
              ))}
            </tr>

            {/* Детальные рейтинги */}
            <CompareRow label="Качество материала" courses={courses} field="avg_content_quality" />
            <CompareRow label="Преподаватели" courses={courses} field="avg_instructors" />
            <CompareRow label="Поддержка" courses={courses} field="avg_support" />
            <CompareRow label="Цена/Качество" courses={courses} field="avg_price_quality" />
            <CompareRow label="Практика" courses={courses} field="avg_practical" />

            {/* Цена */}
            <tr>
              <td className="border p-4 font-semibold">Цена</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center">
                  <span className="text-lg font-bold text-primary-600">
                    {course.price_type === 'free' ? 'Бесплатно' : `${course.price_amount} ${course.currency}`}
                  </span>
                  {course.price_type === 'subscription' && <p className="text-sm text-gray-600">/месяц</p>}
                </td>
              ))}
            </tr>

            {/* Формат */}
            <tr>
              <td className="border p-4 font-semibold">Формат</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center capitalize">
                  {course.format}
                </td>
              ))}
            </tr>

            {/* Длительность */}
            <tr>
              <td className="border p-4 font-semibold">Длительность</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center">
                  {course.duration_weeks ? `${course.duration_weeks} недель` :
                   course.duration_hours ? `${course.duration_hours} часов` : '-'}
                </td>
              ))}
            </tr>

            {/* Сертификат */}
            <tr>
              <td className="border p-4 font-semibold">Сертификат</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center">
                  {course.has_certificate ? '✅ Да' : '❌ Нет'}
                </td>
              ))}
            </tr>

            {/* Язык */}
            <tr>
              <td className="border p-4 font-semibold">Язык</td>
              {courses.map((course) => (
                <td key={course.id} className="border p-4 text-center capitalize">
                  {course.language}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

function CompareRow({ label, courses, field }) {
  const maxValue = Math.max(...courses.map(c => c[field]))

  return (
    <tr>
      <td className="border p-4 font-semibold">{label}</td>
      {courses.map((course) => {
        const value = course[field]
        const isMax = value === maxValue && value > 0

        return (
          <td key={course.id} className="border p-4 text-center">
            <div className="flex items-center justify-center space-x-2">
              <span className={`text-lg font-bold ${isMax ? 'text-green-600' : ''}`}>
                {value.toFixed(1)}
              </span>
              <div className="flex">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    size={16}
                    className={star <= value ? 'text-yellow-500' : 'text-gray-300'}
                    fill={star <= value ? 'currentColor' : 'none'}
                  />
                ))}
              </div>
            </div>
          </td>
        )
      })}
    </tr>
  )
}

export default CompareCoursesPage
