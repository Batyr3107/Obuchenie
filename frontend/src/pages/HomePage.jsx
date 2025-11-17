import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, TrendingUp, Award, Users, Sparkles, Zap, Target, ArrowRight } from 'lucide-react'
import CourseCard from '../components/courses/CourseCard'
import { coursesAPI } from '../services/api'
import { reportError } from '../utils/errorReporter'
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
      reportError(error, { component: 'HomePage', action: 'fetchTopCourses' })
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      window.location.href = `/courses?search=${searchQuery}`
    }
  }

  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-ocean rounded-3xl py-24 px-6 shadow-2xl animate-fade-in">
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-transparent animate-pulse-slow"></div>
        <div className="absolute top-10 right-10 w-72 h-72 bg-white/10 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-10 left-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>

        <div className="relative text-center max-w-5xl mx-auto">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-6 animate-fade-in-down">
            <Sparkles size={18} className="text-yellow-300 mr-2" />
            <span className="text-white font-semibold">Найди свой идеальный курс</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold mb-6 text-white animate-fade-in-up leading-tight">
            Твой путь к знаниям
            <br />
            <span className="bg-clip-text text-transparent bg-gradient-sunset">начинается здесь</span>
          </h1>

          <p className="text-xl md:text-2xl mb-10 text-white/90 max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            Независимая платформа для поиска, сравнения и оценки лучших обучающих программ
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="relative group">
              <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400 group-hover:text-primary-600 transition-colors" size={24} />
              <input
                type="text"
                placeholder="Поиск курса по названию, категории..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-16 pr-6 py-6 rounded-2xl text-gray-900 text-lg focus:outline-none focus:ring-4 focus:ring-white/50 shadow-2xl bg-white/95 backdrop-blur-sm transition-all duration-300 hover:shadow-glow-lg"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 px-8 py-3 bg-gradient-fire text-white rounded-xl font-semibold transition-all duration-300 hover:shadow-xl hover:scale-105"
              >
                Найти
              </button>
            </div>
          </form>

          {/* Quick stats */}
          <div className="flex flex-wrap justify-center gap-8 mt-12 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <div className="text-white/90">
              <div className="text-3xl font-bold">500+</div>
              <div className="text-sm">Курсов</div>
            </div>
            <div className="text-white/90">
              <div className="text-3xl font-bold">10K+</div>
              <div className="text-sm">Отзывов</div>
            </div>
            <div className="text-white/90">
              <div className="text-3xl font-bold">50+</div>
              <div className="text-sm">Категорий</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in">
        <div className="card-glass text-center group">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-ocean rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-glow transition-all duration-300 group-hover:scale-110 group-hover:rotate-6">
              <TrendingUp className="text-white" size={28} />
            </div>
          </div>
          <h3 className="text-4xl font-bold gradient-text mb-3">500+</h3>
          <p className="text-gray-700 font-medium">Курсов в каталоге</p>
          <p className="text-sm text-gray-500 mt-2">Постоянно растущая база</p>
        </div>

        <div className="card-glass text-center group">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-fire rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-glow transition-all duration-300 group-hover:scale-110 group-hover:rotate-6">
              <Users className="text-white" size={28} />
            </div>
          </div>
          <h3 className="text-4xl font-bold gradient-text-fire mb-3">10,000+</h3>
          <p className="text-gray-700 font-medium">Честных отзывов</p>
          <p className="text-sm text-gray-500 mt-2">От реальных студентов</p>
        </div>

        <div className="card-glass text-center group">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-sunset rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-glow transition-all duration-300 group-hover:scale-110 group-hover:rotate-6">
              <Award className="text-white" size={28} />
            </div>
          </div>
          <h3 className="text-4xl font-bold gradient-text mb-3">50+</h3>
          <p className="text-gray-700 font-medium">Категорий обучения</p>
          <p className="text-sm text-gray-500 mt-2">Для любых целей</p>
        </div>
      </section>

      {/* Top Courses */}
      <section className="animate-fade-in">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h2 className="section-title">Топ курсы</h2>
            <p className="text-gray-600 text-lg">Лучшие обучающие программы по мнению студентов</p>
          </div>
          <Link
            to="/courses"
            className="flex items-center space-x-2 px-6 py-3 bg-white/70 backdrop-blur-sm rounded-xl text-primary-600 hover:bg-white hover:shadow-lg font-semibold transition-all duration-300 hover:scale-105 border border-gray-200/50"
          >
            <span>Смотреть все</span>
            <ArrowRight size={20} />
          </Link>
        </div>

        {topCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {topCourses.map((course, index) => (
              <div
                key={course.id}
                className="animate-fade-in-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CourseCard course={course} />
              </div>
            ))}
          </div>
        ) : (
          <div className="card-glass text-center py-16">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <TrendingUp className="text-gray-400" size={40} />
            </div>
            <p className="text-gray-600 text-lg mb-6">Курсы еще не добавлены</p>
            <Link to="/add-course" className="btn btn-primary inline-flex items-center">
              <Sparkles size={18} className="mr-2" />
              Добавить первый курс
            </Link>
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-purple-600 via-primary-600 to-pink-600 rounded-3xl p-16 text-center shadow-2xl animate-fade-in">
        <div className="absolute inset-0 bg-white/5 backdrop-blur-sm"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>

        <div className="relative">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full mb-6">
            <Zap size={18} className="text-yellow-300 mr-2" />
            <span className="text-white font-semibold">Начни прямо сейчас</span>
          </div>

          <h2 className="text-5xl font-bold text-white mb-6">
            Готов добавить свой курс?
          </h2>
          <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
            Зарегистрируйтесь и добавьте свой обучающий курс в наш каталог.
            Получайте отзывы от реальных студентов и улучшайте качество обучения.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              to="/register"
              className="btn bg-white text-primary-600 hover:bg-gray-50 shadow-2xl inline-flex items-center"
            >
              <Sparkles size={18} className="mr-2" />
              Начать бесплатно
            </Link>
            <Link
              to="/courses"
              className="btn bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm border-2 border-white/30 inline-flex items-center"
            >
              Смотреть все курсы
              <ArrowRight size={18} className="ml-2" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
