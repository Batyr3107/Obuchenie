"""
Unit tests for JSON Helper Functions

DRY & TESTABILITY: Проверка переиспользуемых utility функций
"""
import pytest
from app.utils.json_helpers import (
    parse_json_field,
    parse_json_list,
    serialize_to_json,
    parse_multiple_json_fields,
    batch_parse_json_fields
)


class TestParseJsonField:
    """Тесты parse_json_field"""

    @pytest.mark.unit
    def test_parse_valid_json(self):
        """Тест: корректный JSON парсится"""
        result = parse_json_field('["item1", "item2"]')
        assert result == ["item1", "item2"]

    @pytest.mark.unit
    def test_parse_invalid_json(self):
        """Тест: некорректный JSON возвращает default"""
        result = parse_json_field('invalid json', default=[])
        assert result == []

    @pytest.mark.unit
    def test_parse_none_returns_default(self):
        """Тест: None возвращает default"""
        result = parse_json_field(None, default="default")
        assert result == "default"

    @pytest.mark.unit
    def test_parse_empty_string(self):
        """Тест: пустая строка возвращает default"""
        result = parse_json_field('', default=[])
        assert result == []

    @pytest.mark.unit
    def test_parse_json_object(self):
        """Тест: парсинг JSON объекта"""
        result = parse_json_field('{"key": "value"}')
        assert result == {"key": "value"}


class TestParseJsonList:
    """Тесты parse_json_list"""

    @pytest.mark.unit
    def test_parse_valid_list(self):
        """Тест: парсинг массива"""
        result = parse_json_list('["a", "b", "c"]')
        assert result == ["a", "b", "c"]

    @pytest.mark.unit
    def test_parse_invalid_returns_empty_list(self):
        """Тест: некорректный JSON возвращает пустой список"""
        result = parse_json_list('not a list')
        assert result == []

    @pytest.mark.unit
    def test_parse_none_returns_empty_list(self):
        """Тест: None возвращает пустой список"""
        result = parse_json_list(None)
        assert result == []


class TestSerializeToJson:
    """Тесты serialize_to_json"""

    @pytest.mark.unit
    def test_serialize_list(self):
        """Тест: сериализация списка"""
        result = serialize_to_json(["item1", "item2"])
        assert result == '["item1", "item2"]'

    @pytest.mark.unit
    def test_serialize_dict(self):
        """Тест: сериализация словаря"""
        result = serialize_to_json({"key": "value"})
        assert result == '{"key": "value"}'

    @pytest.mark.unit
    def test_serialize_none(self):
        """Тест: None возвращает default"""
        result = serialize_to_json(None, default="null")
        assert result == "null"

    @pytest.mark.unit
    def test_serialize_with_russian(self):
        """Тест: сериализация с кириллицей"""
        result = serialize_to_json(["Привет", "Мир"])
        assert "Привет" in result
        assert "Мир" in result


class TestParseMultipleJsonFields:
    """Тесты parse_multiple_json_fields"""

    @pytest.mark.unit
    def test_parse_multiple_fields(self):
        """Тест: парсинг нескольких полей"""
        # Arrange
        class MockObject:
            def __init__(self):
                self.pros = '["good"]'
                self.cons = '["bad"]'

        obj = MockObject()

        # Act
        parse_multiple_json_fields(obj, ['pros', 'cons'])

        # Assert
        assert obj.pros == ["good"]
        assert obj.cons == ["bad"]

    @pytest.mark.unit
    def test_parse_nonexistent_field(self):
        """Тест: поле не существует - игнорируется"""
        # Arrange
        class MockObject:
            pass

        obj = MockObject()

        # Act (не должно упасть)
        parse_multiple_json_fields(obj, ['nonexistent'])

        # Assert
        assert not hasattr(obj, 'nonexistent')


class TestBatchParseJsonFields:
    """Тесты batch_parse_json_fields"""

    @pytest.mark.unit
    def test_batch_parse_multiple_objects(self):
        """Тест: парсинг списка объектов"""
        # Arrange
        class MockObject:
            def __init__(self, pros, cons):
                self.pros = pros
                self.cons = cons

        objects = [
            MockObject('["a"]', '["b"]'),
            MockObject('["c"]', '["d"]')
        ]

        # Act
        result = batch_parse_json_fields(objects, ['pros', 'cons'])

        # Assert
        assert result[0].pros == ["a"]
        assert result[0].cons == ["b"]
        assert result[1].pros == ["c"]
        assert result[1].cons == ["d"]

    @pytest.mark.unit
    def test_batch_parse_empty_list(self):
        """Тест: пустой список объектов"""
        result = batch_parse_json_fields([], ['pros', 'cons'])
        assert result == []
