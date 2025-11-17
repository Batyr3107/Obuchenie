"""
Unit tests for ReviewService

TESTABILITY: Тестирование бизнес-логики отдельно от HTTP слоя
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException

from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate
from app.models.review import CompletionStatus
from app.models.course import Course
from app.models.user import User


class TestReviewServiceValidation:
    """Тесты валидации создания отзыва"""

    @pytest.mark.unit
    async def test_validate_review_creation_course_not_found(self):
        """Тест: курс не найден"""
        # Arrange
        db_mock = Mock()
        db_mock.query().filter().first.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ReviewService.validate_review_creation(db_mock, course_id=999, user_id=1)

        assert exc_info.value.status_code == 404
        assert "Course not found" in exc_info.value.detail

    @pytest.mark.unit
    async def test_validate_review_creation_duplicate_review(self):
        """Тест: пользователь уже оставлял отзыв"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course)
        existing_review_mock = Mock()

        # Первый вызов возвращает курс, второй - существующий отзыв
        db_mock.query().filter().first.side_effect = [course_mock, existing_review_mock]

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ReviewService.validate_review_creation(db_mock, course_id=1, user_id=1)

        assert exc_info.value.status_code == 400
        assert "already reviewed" in exc_info.value.detail

    @pytest.mark.unit
    async def test_validate_review_creation_success(self):
        """Тест: успешная валидация"""
        # Arrange
        db_mock = Mock()
        course_mock = Mock(spec=Course, id=1, title="Test Course")

        db_mock.query().filter().first.side_effect = [course_mock, None]

        # Act
        result = await ReviewService.validate_review_creation(db_mock, course_id=1, user_id=1)

        # Assert
        assert result == course_mock


class TestReviewServiceRateLimit:
    """Тесты ограничения количества отзывов"""

    @pytest.mark.unit
    @patch('app.services.review_service.settings')
    async def test_check_rate_limit_exceeded(self, settings_mock):
        """Тест: превышен лимит отзывов в день"""
        # Arrange
        settings_mock.REVIEWS_PER_DAY_LIMIT = 5
        db_mock = Mock()
        db_mock.query().filter().count.return_value = 5

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ReviewService.check_rate_limit(db_mock, user_id=1)

        assert exc_info.value.status_code == 429
        assert "Daily review limit" in exc_info.value.detail

    @pytest.mark.unit
    @patch('app.services.review_service.settings')
    async def test_check_rate_limit_not_exceeded(self, settings_mock):
        """Тест: лимит не превышен"""
        # Arrange
        settings_mock.REVIEWS_PER_DAY_LIMIT = 5
        db_mock = Mock()
        db_mock.query().filter().count.return_value = 3

        # Act (не должно выбросить исключение)
        await ReviewService.check_rate_limit(db_mock, user_id=1)


class TestReviewServiceRatingCalculation:
    """Тесты вычисления рейтинга"""

    @pytest.mark.unit
    def test_calculate_overall_rating(self):
        """Тест: правильный расчет среднего рейтинга"""
        # Arrange
        review_data = ReviewCreate(
            course_id=1,
            content_quality=5.0,
            instructors=4.5,
            support=4.0,
            price_quality=4.5,
            practical=5.0,
            review_text="Great course!",
            recommend=True,
            completion_status=CompletionStatus.COMPLETED
        )

        # Act
        rating = ReviewService.calculate_overall_rating(review_data)

        # Assert
        expected = round((5.0 + 4.5 + 4.0 + 4.5 + 5.0) / 5, 2)
        assert rating == expected
        assert rating == 4.6

    @pytest.mark.unit
    def test_calculate_overall_rating_all_same(self):
        """Тест: все оценки одинаковые"""
        # Arrange
        review_data = ReviewCreate(
            course_id=1,
            content_quality=4.0,
            instructors=4.0,
            support=4.0,
            price_quality=4.0,
            practical=4.0,
            review_text="Good course",
            recommend=True,
            completion_status=CompletionStatus.COMPLETED
        )

        # Act
        rating = ReviewService.calculate_overall_rating(review_data)

        # Assert
        assert rating == 4.0


class TestReviewServiceCourseRatingUpdate:
    """Тесты обновления рейтинга курса"""

    @pytest.mark.unit
    def test_update_course_ratings_no_reviews(self):
        """Тест: курс без отзывов"""
        # Arrange
        course_mock = Mock(spec=Course)
        db_mock = Mock()

        stats_mock = Mock(total=0)
        db_mock.query().filter().first.return_value = stats_mock

        # Act
        ReviewService.update_course_ratings(course_mock, db_mock)

        # Assert
        assert course_mock.avg_rating == 0.0
        assert course_mock.total_reviews == 0
        assert course_mock.avg_content_quality == 0.0

    @pytest.mark.unit
    def test_update_course_ratings_with_reviews(self):
        """Тест: обновление рейтингов с отзывами"""
        # Arrange
        course_mock = Mock(spec=Course)
        db_mock = Mock()

        stats_mock = Mock(
            total=10,
            avg_content_quality=4.5,
            avg_instructors=4.3,
            avg_support=4.0,
            avg_price_quality=4.2,
            avg_practical=4.6
        )
        db_mock.query().filter().first.return_value = stats_mock

        # Act
        ReviewService.update_course_ratings(course_mock, db_mock)

        # Assert
        assert course_mock.total_reviews == 10
        assert course_mock.avg_content_quality == 4.5
        assert course_mock.avg_instructors == 4.3
        # Проверяем общий рейтинг
        expected_avg = round((4.5 + 4.3 + 4.0 + 4.2 + 4.6) / 5, 2)
        assert course_mock.avg_rating == expected_avg


class TestReviewServiceCreateReviewInstance:
    """Тесты создания экземпляра отзыва"""

    @pytest.mark.unit
    def test_create_review_instance_minimal(self):
        """Тест: создание отзыва с минимальными данными"""
        # Arrange
        review_data = ReviewCreate(
            course_id=1,
            content_quality=4.0,
            instructors=4.0,
            support=4.0,
            price_quality=4.0,
            practical=4.0,
            review_text="Good course",
            recommend=True,
            completion_status=CompletionStatus.COMPLETED
        )

        # Act
        review = ReviewService.create_review_instance(
            review_data, user_id=1, overall_rating=4.0
        )

        # Assert
        assert review.user_id == 1
        assert review.course_id == 1
        assert review.overall_rating == 4.0
        assert review.review_text == "Good course"
        assert review.pros is None
        assert review.cons is None

    @pytest.mark.unit
    def test_create_review_instance_with_pros_cons(self):
        """Тест: создание отзыва с pros/cons"""
        # Arrange
        review_data = ReviewCreate(
            course_id=1,
            content_quality=4.0,
            instructors=4.0,
            support=4.0,
            price_quality=4.0,
            practical=4.0,
            review_text="Good course",
            pros=["Great content", "Good teachers"],
            cons=["Expensive"],
            recommend=True,
            completion_status=CompletionStatus.COMPLETED
        )

        # Act
        review = ReviewService.create_review_instance(
            review_data, user_id=1, overall_rating=4.0
        )

        # Assert
        assert review.pros == '["Great content", "Good teachers"]'
        assert review.cons == '["Expensive"]'


@pytest.mark.unit
class TestReviewServiceParseJsonFields:
    """Тесты парсинга JSON полей"""

    def test_parse_json_fields_valid(self):
        """Тест: корректный парсинг JSON"""
        # Arrange
        review_mock = Mock(
            pros='["Good", "Nice"]',
            cons='["Expensive"]'
        )

        # Act
        result = ReviewService.parse_json_fields([review_mock])

        # Assert
        assert result[0].pros == ["Good", "Nice"]
        assert result[0].cons == ["Expensive"]

    def test_parse_json_fields_invalid(self):
        """Тест: некорректный JSON заменяется пустым списком"""
        # Arrange
        review_mock = Mock(
            pros='invalid json',
            cons=None
        )

        # Act
        result = ReviewService.parse_json_fields([review_mock])

        # Assert
        assert result[0].pros == []
        assert result[0].cons == []
