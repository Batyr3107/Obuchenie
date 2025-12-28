"""
Security Module (Facade)

SRP: Этот модуль теперь служит фасадом для обратной совместимости.
Реальная логика разделена по модулям:
- password.py - хеширование паролей
- jwt.py - JWT токены
- lockout.py - блокировка аккаунтов
- token_blacklist.py - blacklist токенов

Импортируйте напрямую из подмодулей для новых проектов.
"""

# Re-export password functions
from app.core.password import (
    verify_password,
    get_password_hash,
)

# Re-export JWT functions
from app.core.jwt import (
    create_access_token,
    decode_token,
)

# Re-export lockout functions
from app.core.lockout import (
    record_failed_login,
    get_failed_login_attempts,
    clear_failed_login_attempts,
    is_account_locked,
)

# Re-export token blacklist functions
from app.core.token_blacklist import (
    blacklist_token,
    is_token_blacklisted,
)

# Export all for backward compatibility
__all__ = [
    # Password
    "verify_password",
    "get_password_hash",
    # JWT
    "create_access_token",
    "decode_token",
    # Lockout
    "record_failed_login",
    "get_failed_login_attempts",
    "clear_failed_login_attempts",
    "is_account_locked",
    # Token blacklist
    "blacklist_token",
    "is_token_blacklisted",
]
