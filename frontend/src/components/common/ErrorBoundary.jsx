import { Component } from 'react'
import { AlertTriangle } from 'lucide-react'
import { reportError } from '../../utils/errorReporter'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Report error to error reporting service
    reportError(error, {
      component: 'ErrorBoundary',
      errorInfo: errorInfo?.componentStack,
      boundary: this.props.name || 'root'
    })

    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mx-auto mb-4">
              <AlertTriangle className="text-red-600" size={32} />
            </div>

            <h1 className="text-2xl font-bold text-center text-gray-900 mb-2">
              Что-то пошло не так
            </h1>

            <p className="text-gray-600 text-center mb-6">
              Произошла непредвиденная ошибка. Мы уже работаем над её исправлением.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 p-4 bg-gray-50 rounded border border-gray-200">
                <summary className="cursor-pointer font-semibold text-sm text-gray-700 mb-2">
                  Детали ошибки (только в dev режиме)
                </summary>
                <pre className="text-xs text-red-600 overflow-auto mt-2">
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="flex flex-col space-y-3">
              <button
                onClick={this.handleReset}
                className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                Попробовать снова
              </button>

              <button
                onClick={() => window.location.href = '/'}
                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Вернуться на главную
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
