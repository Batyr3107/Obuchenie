import { useState, useEffect } from 'react'
import { Search } from 'lucide-react'
import { categoriesAPI } from '../../services/api'

function CourseFilters({ filters, onFiltersChange }) {
  const [categories, setCategories] = useState([])

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll()
      setCategories(response.data)
    } catch (error) {
      console.error('Error fetching categories:', error)
    }
  }

  const handleSearchChange = (e) => {
    onFiltersChange({ ...filters, search: e.target.value })
  }

  const handleCategoryChange = (e) => {
    onFiltersChange({
      ...filters,
      category_id: e.target.value ? parseInt(e.target.value) : null
    })
  }

  const handleRatingChange = (e) => {
    onFiltersChange({
      ...filters,
      min_rating: e.target.value ? parseFloat(e.target.value) : null
    })
  }

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
            value={filters.search}
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
        onClick={() => onFiltersChange({ search: '', category_id: null, min_rating: null })}
        className="btn btn-secondary w-full"
      >
        Сбросить фильтры
      </button>
    </div>
  )
}

export default CourseFilters
