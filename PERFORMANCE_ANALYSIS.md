# Performance Analysis Report

**Date**: 2025-12-28
**Analyzed by**: Claude Code AI
**Codebase**: CourseRate (Full-stack application)

---

## Executive Summary

This report identifies performance anti-patterns, N+1 queries, unnecessary re-renders, and inefficient algorithms in the CourseRate codebase. The analysis covers both the backend (FastAPI/SQLAlchemy) and frontend (React) components.

**Overall Assessment**: The codebase demonstrates good awareness of performance with existing optimizations (joinedload, caching, composite indexes), but several opportunities for improvement remain.

---

## Backend Performance Issues

### 1. N+1 Query Problems

#### 1.1 Compare Endpoint - Missing Eager Loading
**File**: `backend/app/api/endpoints/compare.py:31`
**Severity**: Medium

```python
# Current (N+1 prone)
courses = db.query(Course).filter(Course.id.in_(ids)).all()
```

**Problem**: When accessing `course.category` or `course.subcategory` in the response serialization, each access triggers a separate database query.

**Recommended Fix**:
```python
from sqlalchemy.orm import joinedload

courses = db.query(Course).options(
    joinedload(Course.category),
    joinedload(Course.subcategory)
).filter(Course.id.in_(ids)).all()
```

#### 1.2 Categories - Missing Subcategories Eager Loading
**File**: `backend/app/services/category_service.py:43`
**Severity**: Low

```python
# Current
categories = db.query(Category).all()
```

**Problem**: If subcategories are accessed for each category, N+1 queries occur.

**Recommended Fix**:
```python
from sqlalchemy.orm import joinedload

categories = db.query(Category).options(
    joinedload(Category.subcategories)
).all()
```

---

### 2. Inefficient Query Patterns

#### 2.1 Existence Check Using `.first()` Instead of `.exists()`
**File**: `backend/app/services/favorite_service.py:147-152`
**Severity**: Low

```python
# Current (fetches full row)
favorite = db.query(Favorite).filter(
    Favorite.user_id == user_id,
    Favorite.course_id == course_id
).first()
return favorite is not None
```

**Problem**: Retrieves the entire row when only checking existence.

**Recommended Fix**:
```python
from sqlalchemy import exists

exists_query = db.query(exists().where(
    Favorite.user_id == user_id,
    Favorite.course_id == course_id
)).scalar()
return exists_query
```

#### 2.2 Rate Limit Check Using Full Count
**File**: `backend/app/services/review_service.py:82-86`
**Severity**: Low

```python
# Current (counts ALL reviews for the day)
reviews_today = db.query(Review).filter(
    Review.user_id == user_id,
    func.date(Review.created_at) == today
).count()
```

**Problem**: Counts all reviews when we only need to know if count exceeds limit.

**Recommended Fix**:
```python
# More efficient: stop counting once we exceed limit
reviews_today = db.query(Review).filter(
    Review.user_id == user_id,
    func.date(Review.created_at) == today
).limit(settings.REVIEWS_PER_DAY_LIMIT + 1).count()
```

---

### 3. Missing Database Indexes

#### 3.1 Missing Index on `avg_rating`
**File**: `backend/app/models/course.py`
**Severity**: Medium

The `avg_rating` column is frequently used for:
- Filtering (`min_rating` parameter)
- Sorting (`order_by(Course.avg_rating.desc())`)

**Recommended Fix**: Add index to Course model:
```python
__table_args__ = (
    Index('ix_course_category_status', 'category_id', 'status'),
    Index('ix_course_status_created', 'status', 'created_at'),
    Index('ix_course_avg_rating', 'avg_rating'),  # ADD THIS
)
```

#### 3.2 Missing Composite Index for Favorites Lookup
**File**: `backend/app/models/favorite.py`
**Severity**: Low

Frequent queries use `(user_id, course_id)` combination.

**Recommended Fix**: Ensure composite index exists:
```python
__table_args__ = (
    Index('ix_favorite_user_course', 'user_id', 'course_id'),
)
```

---

### 4. Cache Implementation Issues

#### 4.1 SQLAlchemy Object Serialization
**File**: `backend/app/core/cache.py` + `backend/app/services/course_service.py:113`
**Severity**: High

```python
# This will fail or produce incomplete data
cache_manager.set(cache_key, courses, expire=CourseService.CACHE_TTL)
```

**Problem**: SQLAlchemy model instances cannot be directly serialized to JSON. The cache will either fail silently or store incomplete data.

**Recommended Fix**:
1. Convert to dict/Pydantic schema before caching
2. Or use a custom serializer that handles SQLAlchemy objects

```python
# Option 1: Cache dict representation
courses_data = [course.to_dict() for course in courses]
cache_manager.set(cache_key, courses_data, expire=CourseService.CACHE_TTL)

# Option 2: Add to_dict method to models
class Course(Base):
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            # ... other fields
        }
```

#### 4.2 Redis KEYS Command in Production
**File**: `backend/app/core/cache.py:157`
**Severity**: Medium

```python
keys = self.redis_client.keys(f"cache:{pattern}")
```

**Problem**: The `KEYS` command blocks Redis and is O(N) where N is the total number of keys in the database. This can cause performance issues in production.

**Recommended Fix**: Use `SCAN` iterator instead:
```python
def clear_pattern(self, pattern: str) -> int:
    if not self.enabled or not self.redis_client:
        return 0

    try:
        deleted = 0
        cursor = 0
        while True:
            cursor, keys = self.redis_client.scan(
                cursor=cursor,
                match=f"cache:{pattern}",
                count=100
            )
            if keys:
                deleted += self.redis_client.delete(*keys)
            if cursor == 0:
                break
        return deleted
    except Exception as e:
        logger.error(f"Cache clear pattern error: {e}")
        return 0
```

---

### 5. Async/Await Misuse

#### 5.1 Fake Async Methods
**Files**: Multiple service files
**Severity**: Low (cosmetic)

Many methods are marked as `async` but don't use `await`:

```python
# Example from category_service.py
@staticmethod
async def get_all_categories(db: Session) -> List[Category]:
    # No await anywhere in this method
    categories = db.query(Category).all()
    return categories
```

**Impact**: Minimal performance impact, but misleading code. Either make truly async with async database driver or remove async keyword.

---

## Frontend Performance Issues

### 1. Missing Component Memoization

#### 1.1 CourseCard Not Memoized
**File**: `frontend/src/components/courses/CourseCard.jsx`
**Severity**: Medium

```jsx
// Current
function CourseCard({ course, isPremium = false, isTop = false }) {
  // ...
}
export default CourseCard
```

**Problem**: Re-renders on every parent render even if props unchanged.

**Recommended Fix**:
```jsx
import { memo } from 'react'

function CourseCard({ course, isPremium = false, isTop = false }) {
  // ...
}

export default memo(CourseCard)
```

#### 1.2 CourseFilters Not Memoized
**File**: `frontend/src/components/courses/CourseFilters.jsx`
**Severity**: Medium

Same issue - component re-renders unnecessarily.

---

### 2. Missing Input Debouncing

#### 2.1 Search Input Triggers API on Every Keystroke
**File**: `frontend/src/components/courses/CourseFilters.jsx:22-24`
**Severity**: High

```jsx
const handleSearchChange = (e) => {
  onFiltersChange({ ...filters, search: e.target.value })
}
```

**Problem**: Every keystroke triggers `onFiltersChange`, which triggers API request in parent.

**Recommended Fix**:
```jsx
import { useState, useEffect, useCallback } from 'react'
import { debounce } from 'lodash' // or custom debounce

function CourseFilters({ filters, onFiltersChange }) {
  const [localSearch, setLocalSearch] = useState(filters.search)

  // Debounced callback
  const debouncedSearch = useCallback(
    debounce((value) => {
      onFiltersChange({ ...filters, search: value })
    }, 300),
    [filters, onFiltersChange]
  )

  const handleSearchChange = (e) => {
    setLocalSearch(e.target.value)
    debouncedSearch(e.target.value)
  }

  // ...
}
```

---

### 3. Object Reference Issues Causing Re-renders

#### 3.1 Filters Object Recreation
**File**: `frontend/src/pages/CoursesPage.jsx:15-19`
**Severity**: Medium

```jsx
const [filters, setFilters] = useState({
  search: searchParams.get('search') || '',
  category_id: null,
  min_rating: null,
})

useEffect(() => {
  fetchCourses()
}, [filters])  // Triggers on every object reference change
```

**Problem**: Even if filter values are same, new object reference triggers useEffect.

**Recommended Fix**: Use individual state values or deep comparison:
```jsx
// Option 1: Compare values, not references
useEffect(() => {
  fetchCourses()
}, [filters.search, filters.category_id, filters.min_rating])

// Option 2: Use useMemo for stable reference
const memoizedFilters = useMemo(() => ({
  search: filters.search,
  category_id: filters.category_id,
  min_rating: filters.min_rating
}), [filters.search, filters.category_id, filters.min_rating])
```

---

### 4. Missing Request Optimization

#### 4.1 Parallel API Requests
**File**: `frontend/src/pages/CourseDetailPage.jsx:23-26`
**Severity**: Low

```jsx
useEffect(() => {
  fetchCourse()
  fetchReviews()
}, [id])
```

**Problem**: Requests are initiated but not awaited together, and no request cancellation on unmount/re-render.

**Recommended Fix**:
```jsx
useEffect(() => {
  const controller = new AbortController()

  const fetchData = async () => {
    try {
      const [courseRes, reviewsRes] = await Promise.all([
        coursesAPI.getById(id, { signal: controller.signal }),
        reviewsAPI.getAll({ course_id: id }, { signal: controller.signal })
      ])
      setCourse(courseRes.data)
      setReviews(reviewsRes.data)
    } catch (error) {
      if (!controller.signal.aborted) {
        toast.error('Error loading data')
      }
    }
  }

  fetchData()

  return () => controller.abort()
}, [id])
```

---

### 5. Missing List Virtualization

#### 5.1 Large Course Lists
**File**: `frontend/src/pages/CoursesPage.jsx:122-131`
**Severity**: Medium (scales with data)

```jsx
{courses.map((course, index) => (
  <CourseCard course={course} />
))}
```

**Problem**: For large datasets (100+ courses), rendering all at once causes jank.

**Recommended Fix**: Implement virtualization for lists > 50 items:
```jsx
import { FixedSizeGrid } from 'react-window'

// Use virtualized grid for large lists
{courses.length > 50 ? (
  <FixedSizeGrid
    columnCount={3}
    rowCount={Math.ceil(courses.length / 3)}
    columnWidth={300}
    rowHeight={400}
  >
    {({ columnIndex, rowIndex, style }) => {
      const course = courses[rowIndex * 3 + columnIndex]
      return course ? <CourseCard course={course} style={style} /> : null
    }}
  </FixedSizeGrid>
) : (
  // Regular grid for small lists
  courses.map((course) => <CourseCard course={course} />)
)}
```

---

### 6. State Management Inefficiencies

#### 6.1 Categories Fetched On Every Filter Mount
**File**: `frontend/src/components/courses/CourseFilters.jsx:9-11`
**Severity**: Low

```jsx
useEffect(() => {
  fetchCategories()
}, [])
```

**Problem**: Categories rarely change but are fetched every time component mounts.

**Recommended Fix**: Cache in Zustand store or use React Query:
```jsx
// In store.js
export const useCategoriesStore = create((set, get) => ({
  categories: [],
  lastFetched: null,

  fetchCategories: async () => {
    // Only fetch if stale (> 5 min)
    const now = Date.now()
    if (get().lastFetched && now - get().lastFetched < 5 * 60 * 1000) {
      return get().categories
    }

    const response = await categoriesAPI.getAll()
    set({ categories: response.data, lastFetched: now })
    return response.data
  }
}))
```

---

## Summary of Issues by Priority

### High Priority (Fix Soon)
| Issue | Location | Impact |
|-------|----------|--------|
| Cache serialization of SQLAlchemy objects | cache.py + course_service.py | Data loss/corruption |
| Search debouncing missing | CourseFilters.jsx | Excessive API calls |
| Redis KEYS command in production | cache.py:157 | Redis blocking |

### Medium Priority (Fix in Next Sprint)
| Issue | Location | Impact |
|-------|----------|--------|
| N+1 queries in compare endpoint | compare.py:31 | Database load |
| Missing avg_rating index | course.py model | Slow queries |
| Missing component memoization | CourseCard.jsx, CourseFilters.jsx | UI jank |
| Object reference causing re-renders | CoursesPage.jsx | Wasted renders |
| Missing list virtualization | CoursesPage.jsx | UI jank at scale |

### Low Priority (Backlog)
| Issue | Location | Impact |
|-------|----------|--------|
| `.first()` instead of `.exists()` | favorite_service.py | Minor overhead |
| Rate limit full count | review_service.py | Minor overhead |
| Categories N+1 | category_service.py | Minor |
| Fake async methods | Multiple services | Code clarity |
| Missing AbortController | CourseDetailPage.jsx | Potential race conditions |
| Categories refetching | CourseFilters.jsx | Unnecessary requests |

---

## Recommendations

1. **Immediate Actions**:
   - Fix cache serialization by converting SQLAlchemy objects to dicts
   - Add debouncing to search input (300ms delay)
   - Replace Redis KEYS with SCAN

2. **Short-term Actions**:
   - Add missing database indexes
   - Add `React.memo()` to frequently rendered components
   - Fix N+1 queries in compare endpoint

3. **Long-term Improvements**:
   - Consider React Query or SWR for API state management
   - Implement list virtualization for large datasets
   - Consider async SQLAlchemy with proper async driver

---

## Testing Recommendations

After implementing fixes:
1. Use Django Debug Toolbar equivalent for FastAPI to verify query counts
2. Use React DevTools Profiler to verify re-render reduction
3. Load test with k6 or locust to measure API response time improvements
4. Use Chrome DevTools Performance tab to measure frontend rendering improvements
