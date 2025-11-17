from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.base import get_db
from app.schemas.category import (
    CategoryCreate, CategoryResponse, CategoryWithSubcategories,
    SubcategoryCreate, SubcategoryResponse
)
from app.api.dependencies.auth import get_current_admin
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=List[CategoryWithSubcategories])
async def get_categories(db: Session = Depends(get_db)):
    """
    Получение всех категорий с подкатегориями

    CLEAN CODE: Вся бизнес-логика в CategoryService
    PERFORMANCE: Кэширование на 1 час
    """
    categories = await CategoryService.get_all_categories(db)
    return categories


@router.get("/{category_id}", response_model=CategoryWithSubcategories)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Получение категории по ID

    CLEAN CODE: Вся бизнес-логика в CategoryService
    """
    category = await CategoryService.get_category_by_id(db, category_id)
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Создание новой категории (только админы)

    CLEAN CODE: Вся бизнес-логика в CategoryService
    """
    category = await CategoryService.create_category(db, category_data)
    return category


@router.post("/{category_id}/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory(
    category_id: int,
    subcategory_data: SubcategoryCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Создание подкатегории (только админы)

    CLEAN CODE: Вся бизнес-логика в CategoryService
    """
    subcategory = await CategoryService.create_subcategory(db, category_id, subcategory_data)
    return subcategory
