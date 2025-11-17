"""
Unit tests for UserService

TESTABILITY: Тестирование бизнес-логики без HTTP слоя
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.models.user import User


class TestUserServiceRegistration:
    """Тесты регистрации пользователей"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_register_user_success(self):
        """Тест: успешная регистрация"""
        # Arrange
        db_mock = Mock()
        db_mock.query().filter().first.return_value = None  # Email свободен

        user_data = UserCreate(
            email="test@example.com",
            password="testpass123",
            full_name="Test User"
        )

        # Act
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            with patch('app.services.user_service.sanitize_text', return_value="Test User"):
                with patch('app.services.user_service.get_password_hash', return_value="hashed"):
                    user = await UserService.register_user(db_mock, user_data)

        # Assert
        assert db_mock.add.called
        assert db_mock.commit.called
        assert db_mock.refresh.called

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_register_user_duplicate_email(self):
        """Тест: email уже зарегистрирован"""
        # Arrange
        db_mock = Mock()
        existing_user = Mock(spec=User)
        db_mock.query().filter().first.return_value = existing_user  # Email занят

        user_data = UserCreate(
            email="existing@example.com",
            password="testpass123",
            full_name="Test User"
        )

        # Act & Assert
        with patch('app.services.user_service.validate_email', return_value="existing@example.com"):
            with pytest.raises(HTTPException) as exc_info:
                await UserService.register_user(db_mock, user_data)

            assert exc_info.value.status_code == 400
            assert "already registered" in exc_info.value.detail.lower()


class TestUserServiceAuthentication:
    """Тесты аутентификации"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_authenticate_user_success(self):
        """Тест: успешная аутентификация"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.email = "test@example.com"
        user_mock.hashed_password = "hashed_password"
        user_mock.is_active = True

        db_mock.query().filter().first.return_value = user_mock

        # Act
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            with patch('app.services.user_service.verify_password', return_value=True):
                user = await UserService.authenticate_user(db_mock, "test@example.com", "password123")

        # Assert
        assert user == user_mock

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_authenticate_user_wrong_password(self):
        """Тест: неверный пароль"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.hashed_password = "hashed_password"

        db_mock.query().filter().first.return_value = user_mock

        # Act & Assert
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            with patch('app.services.user_service.verify_password', return_value=False):
                with pytest.raises(HTTPException) as exc_info:
                    await UserService.authenticate_user(db_mock, "test@example.com", "wrongpass")

                assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_authenticate_user_not_found(self):
        """Тест: пользователь не найден"""
        # Arrange
        db_mock = Mock()
        db_mock.query().filter().first.return_value = None  # Пользователь не найден

        # Act & Assert
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            with pytest.raises(HTTPException) as exc_info:
                await UserService.authenticate_user(db_mock, "test@example.com", "password")

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_authenticate_user_inactive(self):
        """Тест: пользователь неактивен"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.is_active = False
        user_mock.hashed_password = "hashed_password"

        db_mock.query().filter().first.return_value = user_mock

        # Act & Assert
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            with patch('app.services.user_service.verify_password', return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    await UserService.authenticate_user(db_mock, "test@example.com", "password")

                assert exc_info.value.status_code == 400
                assert "inactive" in exc_info.value.detail.lower()


class TestUserServiceLastLogin:
    """Тесты обновления времени последнего входа"""

    @pytest.mark.unit
    def test_update_last_login(self):
        """Тест: обновление времени последнего входа"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.last_login = None

        # Act
        UserService.update_last_login(db_mock, user_mock)

        # Assert
        assert user_mock.last_login is not None
        assert db_mock.commit.called


class TestUserServiceGetUser:
    """Тесты получения пользователя"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_id_found(self):
        """Тест: получение пользователя по ID"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User, id=1)
        db_mock.query().filter().first.return_value = user_mock

        # Act
        user = await UserService.get_user_by_id(db_mock, 1)

        # Assert
        assert user == user_mock

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_id_not_found(self):
        """Тест: пользователь не найден"""
        # Arrange
        db_mock = Mock()
        db_mock.query().filter().first.return_value = None

        # Act
        user = await UserService.get_user_by_id(db_mock, 999)

        # Assert
        assert user is None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_user_by_email_found(self):
        """Тест: получение пользователя по email"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User, email="test@example.com")
        db_mock.query().filter().first.return_value = user_mock

        # Act
        with patch('app.services.user_service.validate_email', return_value="test@example.com"):
            user = await UserService.get_user_by_email(db_mock, "test@example.com")

        # Assert
        assert user == user_mock


class TestUserServiceUpdateProfile:
    """Тесты обновления профиля"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_user_profile_full_name(self):
        """Тест: обновление имени пользователя"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.full_name = "Old Name"

        # Act
        with patch('app.services.user_service.sanitize_text', return_value="New Name"):
            user = await UserService.update_user_profile(db_mock, user_mock, full_name="New Name")

        # Assert
        assert user_mock.full_name == "New Name"
        assert db_mock.commit.called
        assert db_mock.refresh.called


class TestUserServiceActivation:
    """Тесты активации/деактивации"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_deactivate_user(self):
        """Тест: деактивация пользователя"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.is_active = True

        # Act
        user = await UserService.deactivate_user(db_mock, user_mock)

        # Assert
        assert user_mock.is_active == False
        assert db_mock.commit.called

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_activate_user(self):
        """Тест: активация пользователя"""
        # Arrange
        db_mock = Mock()
        user_mock = Mock(spec=User)
        user_mock.is_active = False

        # Act
        user = await UserService.activate_user(db_mock, user_mock)

        # Assert
        assert user_mock.is_active == True
        assert db_mock.commit.called
