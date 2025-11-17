"""
Category Service

ARCHITECTURE: Бизнес-логика для работы с категориями
PERFORMANCE: Кэширование категорий
"""
from typing import List
from sqlalchemy.orm import Session
from slugify import slugify
from fastapi import HTTPException, status

from app.models.category import Category, Subcategory
from app.schemas.category import CategoryCreate, SubcategoryCreate
from app.core.cache import cache_manager
from app.utils.db_helpers import get_or_404, exists_or_400


class CategoryService:
    """Сервис для работы с категориями"""

    CACHE_KEY_ALL = "all_categories"
    CACHE_TTL = 3600  # 1 час

    @staticmethod
    async def get_all_categories(db: Session) -> List[Category]:
        """
        Получение всех категорий с подкатегориями

        PERFORMANCE: Кэширование на 1 час (категории редко меняются)

        Args:
            db: Database session

        Returns:
            Список категорий
        """
        # Проверка кэша
        cached = cache_manager.get(CategoryService.CACHE_KEY_ALL)
        if cached is not None:
            return cached

        # Получение из БД
        categories = db.query(Category).all()

        # Сохранение в кэш
        cache_manager.set(
            CategoryService.CACHE_KEY_ALL,
            categories,
            expire=CategoryService.CACHE_TTL
        )

        return categories

    @staticmethod
    async def get_category_by_id(db: Session, category_id: int) -> Category:
        """
        Получение категории по ID

        Args:
            db: Database session
            category_id: ID категории

        Returns:
            Категория

        Raises:
            HTTPException: 404 если не найдена
        """
        return get_or_404(db, Category, category_id, "Category not found")

    @staticmethod
    async def create_category(db: Session, category_data: CategoryCreate) -> Category:
        """
        Создание новой категории

        Args:
            db: Database session
            category_data: Данные категории

        Returns:
            Созданная категория

        Raises:
            HTTPException: 400 если slug уже существует
        """
        slug = slugify(category_data.name)

        # Проверка уникальности slug
        exists_or_400(
            db,
            Category,
            "slug",
            slug,
            "Category with this name already exists"
        )

        # Создание категории
        new_category = Category(
            name=category_data.name,
            slug=slug,
            description=category_data.description,
            icon=category_data.icon
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        # Инвалидация кэша
        CategoryService._invalidate_cache()

        return new_category

    @staticmethod
    async def create_subcategory(
        db: Session,
        category_id: int,
        subcategory_data: SubcategoryCreate
    ) -> Subcategory:
        """
        Создание подкатегории

        Args:
            db: Database session
            category_id: ID родительской категории
            subcategory_data: Данные подкатегории

        Returns:
            Созданная подкатегория

        Raises:
            HTTPException: 404 если категория не найдена
        """
        # Проверка существования категории
        category = get_or_404(db, Category, category_id, "Category not found")

        slug = slugify(subcategory_data.name)

        # Создание подкатегории
        new_subcategory = Subcategory(
            name=subcategory_data.name,
            slug=slug,
            category_id=category_id
        )

        db.add(new_subcategory)
        db.commit()
        db.refresh(new_subcategory)

        # Инвалидация кэша (т.к. добавилась подкатегория)
        CategoryService._invalidate_cache()

        return new_subcategory

    @staticmethod
    async def update_category(
        db: Session,
        category_id: int,
        category_data: CategoryCreate
    ) -> Category:
        """
        Обновление категории

        Args:
            db: Database session
            category_id: ID категории
            category_data: Новые данные

        Returns:
            Обновленная категория

        Raises:
            HTTPException: 404 если не найдена
        """
        category = get_or_404(db, Category, category_id, "Category not found")

        # Обновление полей
        category.name = category_data.name
        category.slug = slugify(category_data.name)
        category.description = category_data.description
        category.icon = category_data.icon

        db.commit()
        db.refresh(category)

        # Инвалидация кэша
        CategoryService._invalidate_cache()

        return category

    @staticmethod
    async def delete_category(db: Session, category_id: int) -> None:
        """
        Удаление категории

        Args:
            db: Database session
            category_id: ID категории

        Raises:
            HTTPException: 404 если не найдена
        """
        category = get_or_404(db, Category, category_id, "Category not found")

        db.delete(category)
        db.commit()

        # Инвалидация кэша
        CategoryService._invalidate_cache()

    @staticmethod
    def _invalidate_cache() -> None:
        """Инвалидация кэша категорий"""
        cache_manager.delete(CategoryService.CACHE_KEY_ALL)
