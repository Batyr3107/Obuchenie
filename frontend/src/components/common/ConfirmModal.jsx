/**
 * ConfirmModal Component
 *
 * PRODUCTION-READY: Reusable confirmation modal
 * - Better UX than native confirm() dialog
 * - Accessible with keyboard navigation (Escape to cancel, Enter to confirm)
 * - Customizable title, message, and button labels
 */
import { useEffect } from 'react'
import { X, AlertTriangle, Info, CheckCircle } from 'lucide-react'

function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = 'Подтвердите действие',
  message = 'Вы уверены, что хотите выполнить это действие?',
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  variant = 'warning', // warning, danger, info, success
  confirmButtonClass = ''
}) {
  // Handle keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'Enter') {
        onConfirm()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose, onConfirm])

  if (!isOpen) return null

  // Icon and color based on variant
  const variantConfig = {
    warning: {
      icon: AlertTriangle,
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600',
      confirmClass: confirmButtonClass || 'bg-yellow-600 hover:bg-yellow-700 text-white'
    },
    danger: {
      icon: AlertTriangle,
      iconBg: 'bg-red-100',
      iconColor: 'text-red-600',
      confirmClass: confirmButtonClass || 'bg-red-600 hover:bg-red-700 text-white'
    },
    info: {
      icon: Info,
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      confirmClass: confirmButtonClass || 'bg-blue-600 hover:bg-blue-700 text-white'
    },
    success: {
      icon: CheckCircle,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      confirmClass: confirmButtonClass || 'bg-green-600 hover:bg-green-700 text-white'
    }
  }

  const config = variantConfig[variant] || variantConfig.warning
  const Icon = config.icon

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 pointer-events-auto animate-scale-in"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Закрыть"
          >
            <X size={20} />
          </button>

          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className={`w-16 h-16 ${config.iconBg} rounded-full flex items-center justify-center`}>
              <Icon className={config.iconColor} size={32} />
            </div>
          </div>

          {/* Title */}
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-3">
            {title}
          </h3>

          {/* Message */}
          <p className="text-gray-600 text-center mb-6">
            {message}
          </p>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-semibold"
            >
              {cancelText}
            </button>
            <button
              onClick={() => {
                onConfirm()
                onClose()
              }}
              className={`flex-1 px-4 py-3 rounded-xl transition-colors font-semibold ${config.confirmClass}`}
            >
              {confirmText}
            </button>
          </div>

          {/* Keyboard hints */}
          <div className="mt-4 text-center text-xs text-gray-400">
            <span className="inline-flex items-center space-x-1">
              <kbd className="px-2 py-1 bg-gray-100 rounded">Esc</kbd>
              <span>для отмены</span>
              <span className="mx-2">•</span>
              <kbd className="px-2 py-1 bg-gray-100 rounded">Enter</kbd>
              <span>для подтверждения</span>
            </span>
          </div>
        </div>
      </div>
    </>
  )
}

export default ConfirmModal
