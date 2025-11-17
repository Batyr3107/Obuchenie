"""
Unit tests for CourseService

TESTABILITY: Тестирование бизнес-логики курсов без HTTP
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.services.course_service import CourseService
from app.schemas.course import CourseCreate, CourseUpdate
from app.models.course import Course, CourseStatus


class TestCourseServiceGetCourses:
    """Тесты получения списка курсов"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_courses_default(self):
        """Тест: получение курсов с параметрами по умолчанию"""
        # Arrange
        db_mock = Mock()
        courses_mock = [Mock(spec=Course) for _ in range(5)]
        db_mock.query().options().filter().order_by().offset().limit().all.return_value = courses_mock

        # Act
        courses = await CourseService.get_courses(db_mock)

        # Assert
        assert len(courses) == 5
        assert db_mock.query.called

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_courses_with_category_filter(self):
        """Тест: фильтрация по категории"""
        # Arrange
        db_mock = Mock()
        courses_mock = [Mock(spec=Course)]
        db_mock.query().options().filter().filter().order_by().offset().limit().all.return_value = courses_mock

        # Act
        courses = await CourseService.get_courses(db_mock, category_id=1)

        # Assert
        assert len(courses) == 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_courses_with_search(self):
        """Тест: поиск по названию"""
        # Arrange
        db_mock = Mock()
        courses_mock = [Mock(spec=Course)]
        db_mock.query().options().filter().filter().order_by().offset().limit().all.return_value = courses_mock

        # Act
        courses = await CourseService.get_courses(db_mock, search="Python")

        # Assert
        assert len(courses) == 1


class TestCourseServiceGetCourseById:
    """Тесты получения курса по ID"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_course_by_id_found(self):
        """Тест: курс найден"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1)
        db_mock.query().options().filter().first.return_value = course_mock

        # Act
        course = await CourseService.get_course_by_id(db_mock, 1)

        # Assert
        assert course == course_mock

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_course_by_id_not_found(self):
        """Тест: курс не найден"""
        # Arrange
        db_mock = Mock()
        db_mock.query().options().filter().first.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CourseService.get_course_by_id(db_mock, 999)

        assert exc_info.value.status_code == 404


class TestCourseServiceIncrementViews:
    """Тесты увеличения счетчика просмотров"""

    @pytest.mark.unit
    def test_increment_views(self):
        """Тест: увеличение счетчика просмотров"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course)
        course_mock.views_count = 10

        # Act
        with patch('app.services.course_service.increment_counter') as mock_increment:
            CourseService.increment_views(db_mock, course_mock)

            # Assert
            mock_increment.assert_called_once_with(db_mock, course_mock, "views_count")
            assert db_mock.commit.called


class TestCourseServiceCreateCourse:
    """Тесты создания курса"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_course_success(self):
        """Тест: успешное создание курса"""
        # Arrange
        db_mock = Mock()
        db_mock.query().filter().first.return_value = None  # Slug свободен

        course_data = Mock(spec=CourseCreate)
        course_data.title = "Python Course"
        course_data.category_id = 1
        course_data.subcategory_id = None
        course_data.short_description = "Short desc"
        course_data.full_description = "Full desc"
        course_data.official_url = "https://example.com"
        course_data.logo_url = None
        course_data.format = "online"
        course_data.price_type = "free"
        course_data.price_amount = None
        course_data.currency = None
        course_data.duration_hours = 10
        course_data.duration_weeks = None
        course_data.language = "ru"
        course_data.has_certificate = True
        course_data.difficulty_level = "beginner"
        course_data.requirements = None
        course_data.what_you_learn = None
        course_data.country = None
        course_data.city = None

        # Act
        course = await CourseService.create_course(db_mock, course_data)

        # Assert
        assert db_mock.add.called
        assert db_mock.commit.called
        assert db_mock.refresh.called

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_course_duplicate_slug(self):
        """Тест: slug уже существует"""
        # Arrange
        db_mock = Mock()
        existing_course = Mock(spec=Course)
        db_mock.query().filter().first.return_value = existing_course  # Slug занят

        course_data = Mock(spec=CourseCreate)
        course_data.title = "Existing Course"
        course_data.category_id = 1

        # Act
        course = await CourseService.create_course(db_mock, course_data)

        # Assert - должен добавить category_id к slug
        assert db_mock.add.called


class TestCourseServiceUpdateCourse:
    """Тесты обновления курса"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_update_course_success(self):
        """Тест: успешное обновление курса"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1)

        with patch('app.services.course_service.get_or_404', return_value=course_mock):
            course_data = Mock(spec=CourseUpdate)
            course_data.model_dump.return_value = {"title": "Updated Title"}

            # Act
            course = await CourseService.update_course(db_mock, 1, course_data)

            # Assert
            assert db_mock.commit.called
            assert db_mock.refresh.called


class TestCourseServiceDeleteCourse:
    """Тесты удаления курса"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_delete_course_success(self):
        """Тест: успешное удаление курса"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1)

        # Act
        with patch('app.services.course_service.get_or_404', return_value=course_mock):
            await CourseService.delete_course(db_mock, 1)

            # Assert
            db_mock.delete.assert_called_once_with(course_mock)
            assert db_mock.commit.called


class TestCourseServiceApproveCourse:
    """Тесты одобрения курса"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_approve_course_success(self):
        """Тест: успешное одобрение курса"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1)
        course_mock.status = CourseStatus.PENDING

        # Act
        with patch('app.services.course_service.get_or_404', return_value=course_mock):
            course = await CourseService.approve_course(db_mock, 1)

            # Assert
            assert course_mock.status == CourseStatus.APPROVED
            assert db_mock.commit.called

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_reject_course_success(self):
        """Тест: отклонение курса"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1)
        course_mock.status = CourseStatus.PENDING

        # Act
        with patch('app.services.course_service.get_or_404', return_value=course_mock):
            course = await CourseService.reject_course(db_mock, 1)

            # Assert
            assert course_mock.status == CourseStatus.REJECTED
            assert db_mock.commit.called


class TestCourseServiceGetPendingCourses:
    """Тесты получения курсов на модерации"""

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_pending_courses(self):
        """Тест: получение курсов на модерации"""
        # Arrange
        db_mock = Mock()
        pending_courses = [Mock(spec=Course) for _ in range(3)]
        db_mock.query().options().filter().order_by().offset().limit().all.return_value = pending_courses

        # Act
        courses = await CourseService.get_pending_courses(db_mock)

        # Assert
        assert len(courses) == 3
