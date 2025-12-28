import { useState, useEffect, useCallback, memo, useRef } from 'react'
import { Search } from 'lucide-react'
import { useCategoriesStore } from '../../utils/store'

/**
 * CourseFilters Component
 *
 * PERFORMANCE:
 * - Wrapped with React.memo to prevent unnecessary re-renders
 * - Uses debounced search to reduce API calls (300ms delay)
 * - Categories fetched from Zustand store (cached)
 * - useCallback for stable handler references
 */
const CourseFilters = memo(function CourseFilters({ filters, onFiltersChange }) {
  const { categories, fetchCategories } = useCategoriesStore()
  const [localSearch, setLocalSearch] = useState(filters.search)
  const debounceTimer = useRef(null)

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  // Sync local search with external filter changes
  useEffect(() => {
    setLocalSearch(filters.search)
  }, [filters.search])

  // PERFORMANCE: Debounced search handler - waits 300ms before triggering API call
  const handleSearchChange = useCallback((e) => {
    const value = e.target.value
    setLocalSearch(value)

    // Clear existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }

    // Set new timer for debounced update
    debounceTimer.current = setTimeout(() => {
      onFiltersChange({ ...filters, search: value })
    }, 300)
  }, [filters, onFiltersChange])

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [])

  const handleCategoryChange = useCallback((e) => {
    onFiltersChange({
      ...filters,
      category_id: e.target.value ? parseInt(e.target.value) : null
    })
  }, [filters, onFiltersChange])

  const handleRatingChange = useCallback((e) => {
    onFiltersChange({
      ...filters,
      min_rating: e.target.value ? parseFloat(e.target.value) : null
    })
  }, [filters, onFiltersChange])

  const handleReset = useCallback(() => {
    setLocalSearch('')
    onFiltersChange({ search: '', category_id: null, min_rating: null })
  }, [onFiltersChange])

  return (
    <div className="card mb-6">
      <h2 className="text-xl font-bold mb-4">Фильтры</h2>

      {/* Search */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Поиск</label>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Название курса..."
            value={localSearch}
            onChange={handleSearchChange}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Category */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Категория</label>
        <select
          value={filters.category_id || ''}
          onChange={handleCategoryChange}
          className="input"
        >
          <option value="">Все категории</option>
          {categories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      {/* Rating */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Минимальный рейтинг</label>
        <select
          value={filters.min_rating || ''}
          onChange={handleRatingChange}
          className="input"
        >
          <option value="">Любой</option>
          <option value="4.5">4.5 и выше</option>
          <option value="4.0">4.0 и выше</option>
          <option value="3.5">3.5 и выше</option>
          <option value="3.0">3.0 и выше</option>
        </select>
      </div>

      {/* Reset */}
      <button
        onClick={handleReset}
        className="btn btn-secondary w-full"
      >
        Сбросить фильтры
      </button>
    </div>
  )
})

export default CourseFilters
