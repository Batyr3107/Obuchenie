"""
Database configuration with optimized connection pooling
"""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import DisconnectionError
from typing import Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# ============= Engine Configuration =============

# Connection pool settings based on environment
if settings.is_production():
    pool_class = pool.QueuePool
    pool_config = {
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,  # Enable pessimistic disconnect handling
    }
else:
    # For development, use simpler pooling
    pool_class = pool.QueuePool
    pool_config = {
        "pool_size": 2,
        "max_overflow": 3,
        "pool_timeout": 10,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }

# Create engine with optimized settings
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=pool_class,
    echo=settings.DB_ECHO,
    echo_pool=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
    future=True,  # Use SQLAlchemy 2.0 style
    **pool_config
)


# ============= Event Listeners =============

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event listener for new connections"""
    logger.debug("Database connection established")

    # Set connection-level settings for PostgreSQL
    if "postgresql" in str(engine.url):
        cursor = dbapi_conn.cursor()
        # Set statement timeout (30 seconds)
        cursor.execute("SET statement_timeout = 30000")
        # Set timezone
        cursor.execute("SET timezone = 'UTC'")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Event listener when connection is checked out from pool"""
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Event listener when connection is returned to pool"""
    logger.debug("Connection returned to pool")


@event.listens_for(pool.Pool, "close")
def receive_close(dbapi_conn, connection_record):
    """Event listener when connection is closed"""
    logger.debug("Connection closed")


@event.listens_for(pool.Pool, "invalidate")
def receive_invalidate(dbapi_conn, connection_record, exception):
    """Event listener when connection is invalidated"""
    logger.warning(f"Connection invalidated: {exception}")


# ============= Session Configuration =============

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Don't expire objects after commit
)

# Declarative Base
Base = declarative_base()


# ============= Database Dependency =============

def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии БД

    Yields:
        Session: SQLAlchemy database session

    Example:
        @router.get("/items")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except DisconnectionError:
        logger.error("Database disconnection error, attempting reconnect")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ============= Database Utilities =============

def check_database_connection() -> bool:
    """
    Check if database connection is healthy

    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_connection_pool_status() -> dict:
    """
    Get current connection pool statistics

    Returns:
        dict: Pool statistics including size, overflow, etc.
    """
    pool_obj = engine.pool
    return {
        "pool_size": pool_obj.size(),
        "checked_in": pool_obj.checkedin(),
        "checked_out": pool_obj.checkedout(),
        "overflow": pool_obj.overflow(),
        "max_overflow": pool_config.get("max_overflow", 0),
        "total": pool_obj.size() + pool_obj.overflow(),
    }


def dispose_engine():
    """
    Dispose all connections in the pool
    Useful for graceful shutdown
    """
    logger.info("Disposing database engine")
    engine.dispose()


# ============= Context Managers =============

class DatabaseTransaction:
    """
    Context manager for database transactions

    Usage:
        with DatabaseTransaction() as session:
            session.add(new_object)
            # Automatically commits on success, rollbacks on error
    """

    def __init__(self):
        self.session: Session = SessionLocal()

    def __enter__(self) -> Session:
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Transaction rollback: {exc_val}")
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()


# ============= Startup/Shutdown Handlers =============

def init_db():
    """
    Initialize database
    Create all tables if they don't exist
    """
    logger.info("Initializing database")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def close_db():
    """
    Close all database connections
    Called during application shutdown
    """
    logger.info("Closing database connections")
    dispose_engine()
    logger.info("Database connections closed")


# ============= Health Check =============

async def database_health_check() -> dict:
    """
    Comprehensive database health check

    Returns:
        dict: Health check results
    """
    result = {
        "healthy": False,
        "connection": False,
        "pool_status": None,
        "error": None
    }

    try:
        # Check connection
        result["connection"] = check_database_connection()

        # Get pool status
        result["pool_status"] = get_connection_pool_status()

        # Overall health
        result["healthy"] = result["connection"]

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        result["error"] = str(e)

    return result
