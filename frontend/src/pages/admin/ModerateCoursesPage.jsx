import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, X, ExternalLink } from 'lucide-react'
import { useAuthStore } from '../../utils/store'
import ConfirmModal from '../../components/common/ConfirmModal'
import api from '../../services/api'
import toast from 'react-hot-toast'

function ModerateCoursesPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [confirmModal, setConfirmModal] = useState({ isOpen: false, courseId: null })

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/')
      return
    }
    fetchPendingCourses()
  }, [user, navigate])

  const fetchPendingCourses = async () => {
    try {
      const response = await api.get('/admin/courses/pending')
      setCourses(response.data)
    } catch (error) {
      toast.error('Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (courseId) => {
    try {
      await api.post(`/admin/courses/${courseId}/approve`)
      toast.success('Курс одобрен!')
      setCourses(courses.filter(c => c.id !== courseId))
    } catch (error) {
      toast.error('Ошибка')
    }
  }

  const handleReject = (courseId) => {
    setConfirmModal({ isOpen: true, courseId })
  }

  const confirmReject = async () => {
    const { courseId } = confirmModal

    try {
      await api.post(`/admin/courses/${courseId}/reject`)
      toast.success('Курс отклонен')
      setCourses(courses.filter(c => c.id !== courseId))
    } catch (error) {
      toast.error('Ошибка')
    }
  }

  if (loading) {
    return <div className="text-center py-12">Загрузка...</div>
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Модерация курсов</h1>

      {courses.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-600">Нет курсов на модерации 🎉</p>
        </div>
      ) : (
        <div className="space-y-6">
          {courses.map((course) => (
            <div key={course.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-2">{course.title}</h3>
                  <p className="text-gray-600 mb-4">{course.short_description}</p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Формат</p>
                      <p className="font-semibold">{course.format}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Цена</p>
                      <p className="font-semibold">
                        {course.price_type === 'free' ? 'Бесплатно' : `${course.price_amount} ${course.currency}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Язык</p>
                      <p className="font-semibold">{course.language}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Сертификат</p>
                      <p className="font-semibold">{course.has_certificate ? 'Да' : 'Нет'}</p>
                    </div>
                  </div>

                  <a
                    href={course.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                  >
                    <span>Посетить сайт курса</span>
                    <ExternalLink size={16} />
                  </a>
                </div>

                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => handleApprove(course.id)}
                    className="btn btn-primary flex items-center space-x-2"
                  >
                    <Check size={18} />
                    <span>Одобрить</span>
                  </button>

                  <button
                    onClick={() => handleReject(course.id)}
                    className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center space-x-2"
                  >
                    <X size={18} />
                    <span>Отклонить</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, courseId: null })}
        onConfirm={confirmReject}
        title="Отклонить курс?"
        message="Вы уверены, что хотите отклонить этот курс? Это действие нельзя отменить."
        confirmText="Да, отклонить"
        cancelText="Отмена"
        variant="danger"
      />
    </div>
  )
}

export default ModerateCoursesPage
