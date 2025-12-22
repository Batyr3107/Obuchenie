import { create } from 'zustand'
import { authAPI } from '../services/api'

/**
 * Auth Store
 *
 * Best Practice: Centralized auth state management with event-based logout
 * for handling 401 responses from API interceptor.
 */
export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),

  // Initialize auth event listener (call this in App.jsx useEffect)
  initAuthListener: () => {
    const handleLogout = () => {
      get().logout()
      // Navigate will be handled by component watching isAuthenticated
    }
    window.addEventListener('auth:logout', handleLogout)
    return () => window.removeEventListener('auth:logout', handleLogout)
  },

  login: async (email, password) => {
    try {
      const response = await authAPI.login(email, password)
      const { access_token } = response.data
      localStorage.setItem('token', access_token)

      const userResponse = await authAPI.getCurrentUser()
      set({
        token: access_token,
        user: userResponse.data,
        isAuthenticated: true
      })

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Ошибка входа'
      }
    }
  },

  register: async (data) => {
    try {
      await authAPI.register(data)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Ошибка регистрации'
      }
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    try {
      const response = await authAPI.getCurrentUser()
      set({ user: response.data })
    } catch (error) {
      set({ user: null, token: null, isAuthenticated: false })
      localStorage.removeItem('token')
    }
  },
}))

export const useCoursesStore = create((set) => ({
  courses: [],
  currentCourse: null,
  filters: {
    search: '',
    category_id: null,
    min_rating: null,
  },

  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),

  setCourses: (courses) => set({ courses }),
  setCurrentCourse: (course) => set({ currentCourse: course }),
}))

export const useThemeStore = create((set) => ({
  theme: localStorage.getItem('theme') || 'light',

  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
    return { theme: newTheme }
  }),

  setTheme: (theme) => set(() => {
    localStorage.setItem('theme', theme)
    document.documentElement.classList.toggle('dark', theme === 'dark')
    return { theme }
  }),
}))
