import { Link } from 'react-router-dom'
import { Github, Twitter, Mail } from 'lucide-react'

function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-bold mb-4">CourseRate</h3>
            <p className="text-sm">
              Независимая платформа для поиска, сравнения и оценки обучающих программ.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Платформа</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/courses" className="hover:text-white transition">Все курсы</Link></li>
              <li><Link to="/categories" className="hover:text-white transition">Категории</Link></li>
              <li><Link to="/add-course" className="hover:text-white transition">Добавить курс</Link></li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-white font-semibold mb-4">Информация</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="hover:text-white transition">О проекте</Link></li>
              <li><Link to="/how-it-works" className="hover:text-white transition">Как это работает</Link></li>
              <li><Link to="/pricing" className="hover:text-white transition">Тарифы</Link></li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="text-white font-semibold mb-4">Контакты</h4>
            <div className="flex space-x-4">
              <a href="#" className="hover:text-white transition">
                <Github size={20} />
              </a>
              <a href="#" className="hover:text-white transition">
                <Twitter size={20} />
              </a>
              <a href="#" className="hover:text-white transition">
                <Mail size={20} />
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
          <p>&copy; 2024 CourseRate. Все права защищены.</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
