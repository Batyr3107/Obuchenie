"""
Sorting Strategies Module

OCP: Добавление новых стратегий сортировки не требует изменения
существующего кода. Просто добавьте новую запись в словарь.

Usage:
    from app.utils.sorting import REVIEW_SORT_STRATEGIES, apply_sort

    query = apply_sort(query, "recent", REVIEW_SORT_STRATEGIES)
"""
from typing import Callable, Dict, Any
from sqlalchemy.orm import Query

from app.models.review import Review


# Type alias for sort strategy function
SortStrategy = Callable[[Query], Query]


# ============ REVIEW SORT STRATEGIES ============
# OCP: Add new sort options here without modifying other code

REVIEW_SORT_STRATEGIES: Dict[str, SortStrategy] = {
    "recent": lambda q: q.order_by(Review.created_at.desc()),
    "oldest": lambda q: q.order_by(Review.created_at.asc()),
    "helpful": lambda q: q.order_by(Review.helpful_count.desc()),
    "rating_high": lambda q: q.order_by(Review.overall_rating.desc()),
    "rating_low": lambda q: q.order_by(Review.overall_rating.asc()),
}

# Default sort if not specified
DEFAULT_REVIEW_SORT = "recent"


def apply_sort(
    query: Query,
    sort_key: str,
    strategies: Dict[str, SortStrategy],
    default: str = "recent"
) -> Query:
    """
    Apply sorting strategy to query.

    OCP: This function is closed for modification but open for extension
    via the strategies dictionary.

    Args:
        query: SQLAlchemy query
        sort_key: Key of sorting strategy
        strategies: Dictionary of available strategies
        default: Default strategy if key not found

    Returns:
        Query with applied sorting

    Example:
        query = apply_sort(query, "helpful", REVIEW_SORT_STRATEGIES)
    """
    strategy = strategies.get(sort_key, strategies.get(default))
    if strategy:
        return strategy(query)
    return query


def get_available_sorts(strategies: Dict[str, SortStrategy]) -> list:
    """
    Get list of available sort options.

    Useful for API documentation and validation.

    Args:
        strategies: Dictionary of strategies

    Returns:
        List of sort keys
    """
    return list(strategies.keys())


# ============ COURSE SORT STRATEGIES ============
# Example of extension for courses

def _create_course_strategies():
    """Factory for course sort strategies (lazy import to avoid circular deps)"""
    from app.models.course import Course

    return {
        "rating": lambda q: q.order_by(Course.avg_rating.desc()),
        "reviews": lambda q: q.order_by(Course.total_reviews.desc()),
        "newest": lambda q: q.order_by(Course.created_at.desc()),
        "views": lambda q: q.order_by(Course.views_count.desc()),
        "favorites": lambda q: q.order_by(Course.favorites_count.desc()),
    }


# Lazy initialization
_course_strategies = None


def get_course_sort_strategies() -> Dict[str, SortStrategy]:
    """Get course sort strategies (lazy initialized)"""
    global _course_strategies
    if _course_strategies is None:
        _course_strategies = _create_course_strategies()
    return _course_strategies
