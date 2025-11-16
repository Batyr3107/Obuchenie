from pydantic import BaseModel
from typing import Optional, List


# Category
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]

    class Config:
        from_attributes = True


# Subcategory
class SubcategoryCreate(BaseModel):
    name: str
    category_id: int


class SubcategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    category_id: int

    class Config:
        from_attributes = True


# Category with subcategories
class CategoryWithSubcategories(CategoryResponse):
    subcategories: List[SubcategoryResponse] = []

    class Config:
        from_attributes = True
