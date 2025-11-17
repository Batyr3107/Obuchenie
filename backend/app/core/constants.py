"""
Application constants and enumerations
Centralized location for all application-wide constants
"""
from enum import Enum


# ============= HTTP Status Codes =============
class HTTPStatus:
    """HTTP Status codes"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500


# ============= Error Messages =============
class ErrorMessages:
    """Centralized error messages"""
    # Authentication
    INVALID_CREDENTIALS = "Invalid email or password"
    UNAUTHORIZED = "Authentication required"
    FORBIDDEN = "You don't have permission to access this resource"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"

    # Validation
    VALIDATION_ERROR = "Validation error"
    INVALID_INPUT = "Invalid input data"
    MISSING_REQUIRED_FIELD = "Missing required field"

    # Resources
    NOT_FOUND = "Resource not found"
    ALREADY_EXISTS = "Resource already exists"
    COURSE_NOT_FOUND = "Course not found"
    USER_NOT_FOUND = "User not found"
    REVIEW_NOT_FOUND = "Review not found"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later"
    DAILY_LIMIT_EXCEEDED = "Daily limit exceeded"

    # Database
    DATABASE_ERROR = "Database error occurred"
    INTEGRITY_ERROR = "Data integrity constraint violated"

    # Server
    INTERNAL_ERROR = "Internal server error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"


# ============= Success Messages =============
class SuccessMessages:
    """Centralized success messages"""
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    REGISTRATION_SUCCESS = "Registration successful"
    EMAIL_SENT = "Email sent successfully"


# ============= Regex Patterns =============
class RegexPatterns:
    """Common regex patterns"""
    EMAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    PHONE = r'^\+?1?\d{9,15}$'
    URL = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    UUID = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    SLUG = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'


# ============= Cache Keys =============
class CacheKeys:
    """Redis cache key prefixes"""
    COURSE = "course"
    COURSES_LIST = "courses_list"
    COURSE_REVIEWS = "course_reviews"
    CATEGORIES = "categories"
    USER_FAVORITES = "user_favorites"
    SEARCH_RESULTS = "search_results"
    STATISTICS = "statistics"


# ============= Cache Timeouts (seconds) =============
class CacheTimeout:
    """Cache expiration times in seconds"""
    MINUTE = 60
    FIVE_MINUTES = 300
    TEN_MINUTES = 600
    THIRTY_MINUTES = 1800
    HOUR = 3600
    DAY = 86400
    WEEK = 604800

    # Specific use cases
    COURSE_DETAIL = THIRTY_MINUTES
    COURSES_LIST = TEN_MINUTES
    CATEGORIES = DAY
    SEARCH = FIVE_MINUTES
    STATISTICS = HOUR


# ============= Pagination =============
class Pagination:
    """Pagination constants"""
    MIN_PAGE = 1
    MIN_PAGE_SIZE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


# ============= Rating =============
class Rating:
    """Rating constants"""
    MIN = 1
    MAX = 5
    CRITERIA_COUNT = 5  # Number of rating criteria


# ============= File Upload =============
class FileUpload:
    """File upload constants"""
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']


# ============= Limits =============
class Limits:
    """Various application limits"""
    # Review
    REVIEW_TEXT_MIN_LENGTH = 50
    REVIEW_TEXT_MAX_LENGTH = 5000
    REVIEW_PROS_MAX_ITEMS = 10
    REVIEW_CONS_MAX_ITEMS = 10
    REVIEW_ITEM_MAX_LENGTH = 500

    # Course
    COURSE_TITLE_MIN_LENGTH = 10
    COURSE_TITLE_MAX_LENGTH = 255
    COURSE_DESCRIPTION_MIN_LENGTH = 100
    COURSE_DESCRIPTION_MAX_LENGTH = 10000

    # User
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    FULL_NAME_MAX_LENGTH = 200

    # Search
    SEARCH_QUERY_MIN_LENGTH = 2
    SEARCH_QUERY_MAX_LENGTH = 100


# ============= Date Formats =============
class DateFormats:
    """Standard date/time formats"""
    DATE = "%Y-%m-%d"
    TIME = "%H:%M:%S"
    DATETIME = "%Y-%m-%d %H:%M:%S"
    DATETIME_ISO = "%Y-%m-%dT%H:%M:%S"
    DATE_DISPLAY = "%d %b %Y"
    DATETIME_DISPLAY = "%d %b %Y %H:%M"


# ============= Headers =============
class Headers:
    """Custom HTTP headers"""
    REQUEST_ID = "X-Request-ID"
    CORRELATION_ID = "X-Correlation-ID"
    API_KEY = "X-API-Key"
    USER_AGENT = "User-Agent"
    FORWARDED_FOR = "X-Forwarded-For"
    REAL_IP = "X-Real-IP"


# ============= Queue Names =============
class QueueNames:
    """Celery queue names"""
    DEFAULT = "default"
    EMAIL = "email"
    NOTIFICATIONS = "notifications"
    REPORTS = "reports"
    ANALYTICS = "analytics"


# ============= Email Templates =============
class EmailTemplates:
    """Email template identifiers"""
    WELCOME = "welcome"
    VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    NEW_REVIEW = "new_review"
    REVIEW_APPROVED = "review_approved"
    REVIEW_REJECTED = "review_rejected"


# ============= Roles & Permissions =============
class Permissions:
    """Permission constants"""
    # Review permissions
    CREATE_REVIEW = "review:create"
    EDIT_OWN_REVIEW = "review:edit_own"
    DELETE_OWN_REVIEW = "review:delete_own"
    MODERATE_REVIEWS = "review:moderate"

    # Course permissions
    CREATE_COURSE = "course:create"
    EDIT_OWN_COURSE = "course:edit_own"
    DELETE_OWN_COURSE = "course:delete_own"
    MODERATE_COURSES = "course:moderate"

    # Admin permissions
    MANAGE_USERS = "admin:manage_users"
    VIEW_STATISTICS = "admin:view_stats"
    MANAGE_CATEGORIES = "admin:manage_categories"


# ============= Timeouts =============
class Timeouts:
    """Various timeout constants (in seconds)"""
    HTTP_REQUEST = 30
    DATABASE_QUERY = 30
    REDIS_CONNECTION = 5
    CACHE_LOCK = 10
    API_CALL = 60


# ============= Retry Settings =============
class RetrySettings:
    """Retry configuration"""
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    BACKOFF_FACTOR = 2  # exponential backoff multiplier


# ============= Feature Flags =============
class FeatureFlags:
    """Feature flag constants"""
    ENABLE_CACHING = "enable_caching"
    ENABLE_RATE_LIMITING = "enable_rate_limiting"
    ENABLE_EMAIL_NOTIFICATIONS = "enable_email_notifications"
    ENABLE_TELEGRAM_BOT = "enable_telegram_bot"
    ENABLE_PREMIUM_FEATURES = "enable_premium_features"
    ENABLE_TWO_FACTOR_AUTH = "enable_2fa"
