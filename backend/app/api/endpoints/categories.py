from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from slugify import slugify

from app.db.base import get_db
from app.models.category import Category, Subcategory
from app.schemas.category import (
    CategoryCreate, CategoryResponse, CategoryWithSubcategories,
    SubcategoryCreate, SubcategoryResponse
)
from app.api.dependencies.auth import get_current_admin

router = APIRouter()


@router.get("/", response_model=List[CategoryWithSubcategories])
async def get_categories(db: Session = Depends(get_db)):
    """Получение всех категорий с подкатегориями"""
    categories = db.query(Category).all()
    return categories


@router.get("/{category_id}", response_model=CategoryWithSubcategories)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Получение категории по ID"""
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание новой категории (только админы)"""

    slug = slugify(category_data.name)

    # Проверка уникальности
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    new_category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        icon=category_data.icon
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.post("/{category_id}/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_subcategory(
    category_id: int,
    subcategory_data: SubcategoryCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Создание подкатегории (только админы)"""

    # Проверка существования категории
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    slug = slugify(subcategory_data.name)

    new_subcategory = Subcategory(
        name=subcategory_data.name,
        slug=slug,
        category_id=category_id
    )

    db.add(new_subcategory)
    db.commit()
    db.refresh(new_subcategory)

    return new_subcategory
