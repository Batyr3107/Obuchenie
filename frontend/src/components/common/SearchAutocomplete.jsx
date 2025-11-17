import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import api from '../../services/api'
import { reportError } from '../../utils/errorReporter'

function SearchAutocomplete() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)
  const wrapperRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (query.length >= 2) {
      const timer = setTimeout(() => {
        fetchSuggestions()
      }, 300) // Debounce
      return () => clearTimeout(timer)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [query])

  const fetchSuggestions = async () => {
    try {
      setLoading(true)
      const response = await api.get('/search/autocomplete', {
        params: { q: query }
      })
      setSuggestions(response.data)
      setShowSuggestions(true)
    } catch (error) {
      reportError(error, { component: 'SearchAutocomplete', action: 'fetchSuggestions', query })
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (courseId) => {
    navigate(`/courses/${courseId}`)
    setShowSuggestions(false)
    setQuery('')
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/courses?search=${query}`)
      setShowSuggestions(false)
    }
  }

  return (
    <div ref={wrapperRef} className="relative w-full max-w-2xl">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <Search
            className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"
            size={20}
          />
          <input
            type="text"
            placeholder="Поиск курсов..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query.length >= 2 && setShowSuggestions(true)}
            className="w-full pl-12 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-2 bg-white rounded-lg shadow-lg border border-gray-200 max-h-80 overflow-y-auto">
          {loading && (
            <div className="p-4 text-center text-gray-500">Поиск...</div>
          )}

          {!loading && suggestions.map((item) => (
            <button
              key={item.id}
              onClick={() => handleSelect(item.id)}
              className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b last:border-b-0 transition"
            >
              <div className="flex items-center space-x-3">
                <Search size={16} className="text-gray-400" />
                <span className="font-medium">{item.title}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchAutocomplete
