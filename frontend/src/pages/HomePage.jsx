import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, TrendingUp, Award, Users } from 'lucide-react'
import CourseCard from '../components/courses/CourseCard'
import { coursesAPI } from '../services/api'
import toast from 'react-hot-toast'

function HomePage() {
  const [topCourses, setTopCourses] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchTopCourses()
  }, [])

  const fetchTopCourses = async () => {
    try {
      const response = await coursesAPI.getAll({ limit: 6, min_rating: 4.0 })
      setTopCourses(response.data)
    } catch (error) {
      console.error('Error fetching courses:', error)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      window.location.href = `/courses?search=${searchQuery}`
    }
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-20 rounded-lg mb-12">
        <div className="text-center max-w-4xl mx-auto px-4">
          <h1 className="text-5xl font-bold mb-6">
            Найди лучший курс для обучения
          </h1>
          <p className="text-xl mb-8 text-gray-100">
            Независимая платформа для поиска, сравнения и оценки обучающих программ
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={24} />
              <input
                type="text"
                placeholder="Поиск курса по названию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-lg text-gray-900 text-lg focus:outline-none focus:ring-4 focus:ring-primary-300"
              />
            </div>
          </form>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="card text-center">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
              <TrendingUp className="text-primary-600" size={24} />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">500+</h3>
          <p className="text-gray-600">Курсов в каталоге</p>
        </div>

        <div className="card text-center">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <Users className="text-green-600" size={24} />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">10,000+</h3>
          <p className="text-gray-600">Честных отзывов</p>
        </div>

        <div className="card text-center">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-gold-100 rounded-full flex items-center justify-center">
              <Award className="text-gold-600" size={24} />
            </div>
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-2">50+</h3>
          <p className="text-gray-600">Категорий обучения</p>
        </div>
      </section>

      {/* Top Courses */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-gray-900">Топ курсы</h2>
          <Link to="/courses" className="text-primary-600 hover:text-primary-700 font-semibold">
            Смотреть все →
          </Link>
        </div>

        {topCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        ) : (
          <div className="card text-center py-12">
            <p className="text-gray-600">Курсы еще не добавлены</p>
            <Link to="/add-course" className="btn btn-primary mt-4 inline-block">
              Добавить первый курс
            </Link>
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section className="bg-gray-100 rounded-lg p-12 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Хотите добавить свой курс?
        </h2>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Зарегистрируйтесь и добавьте свой обучающий курс в наш каталог.
          Получайте отзывы от реальных студентов и улучшайте качество обучения.
        </p>
        <Link to="/register" className="btn btn-primary">
          Начать бесплатно
        </Link>
      </section>
    </div>
  )
}

export default HomePage
