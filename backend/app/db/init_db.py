"""
Скрипт инициализации базы данных с начальными данными
"""
from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine, Base
from app.models import User, Category, Subcategory
from app.core.security import get_password_hash
from app.core.config import settings
from slugify import slugify


def init_categories(db: Session):
    """Создание начальных категорий"""
    categories_data = [
        {
            "name": "IT и программирование",
            "description": "Курсы по веб-разработке, мобильной разработке, Data Science и другим IT направлениям",
            "icon": "code",
            "subcategories": [
                "Веб-разработка",
                "Мобильная разработка",
                "Data Science / AI",
                "DevOps",
                "Тестирование",
                "Кибербезопасность"
            ]
        },
        {
            "name": "Дизайн и творчество",
            "description": "Графический дизайн, UX/UI, 3D моделирование и анимация",
            "icon": "palette",
            "subcategories": [
                "Графический дизайн",
                "UX/UI дизайн",
                "3D и анимация",
                "Фотография и видео"
            ]
        },
        {
            "name": "Бизнес и управление",
            "description": "Менеджмент, предпринимательство, финансы",
            "icon": "briefcase",
            "subcategories": [
                "Менеджмент",
                "Предпринимательство",
                "Финансы и инвестиции",
                "HR и рекрутинг"
            ]
        },
        {
            "name": "Маркетинг и продажи",
            "description": "Digital-маркетинг, SMM, контент-маркетинг",
            "icon": "megaphone",
            "subcategories": [
                "Digital-маркетинг",
                "SMM",
                "Контент-маркетинг",
                "Продажи"
            ]
        },
        {
            "name": "Иностранные языки",
            "description": "Изучение английского, китайского и других языков",
            "icon": "globe",
            "subcategories": [
                "Английский язык",
                "Китайский язык",
                "Другие языки"
            ]
        },
        {
            "name": "Личностный рост",
            "description": "Психология, коммуникация, продуктивность",
            "icon": "heart",
            "subcategories": [
                "Психология",
                "Коммуникация",
                "Продуктивность"
            ]
        }
    ]

    for cat_data in categories_data:
        # Проверка существования категории
        existing = db.query(Category).filter(Category.slug == slugify(cat_data["name"])).first()
        if existing:
            print(f"Category '{cat_data['name']}' already exists, skipping...")
            continue

        # Создание категории
        category = Category(
            name=cat_data["name"],
            slug=slugify(cat_data["name"]),
            description=cat_data.get("description"),
            icon=cat_data.get("icon")
        )
        db.add(category)
        db.flush()

        # Создание подкатегорий
        for subcat_name in cat_data.get("subcategories", []):
            subcategory = Subcategory(
                name=subcat_name,
                slug=slugify(subcat_name),
                category_id=category.id
            )
            db.add(subcategory)

        print(f"✅ Created category: {cat_data['name']} with {len(cat_data.get('subcategories', []))} subcategories")

    db.commit()


def init_admin(db: Session):
    """Создание администратора"""
    from app.models.user import UserRole

    # Проверка существования админа
    admin_email = settings.FIRST_SUPERUSER_EMAIL
    existing_admin = db.query(User).filter(User.email == admin_email).first()

    if existing_admin:
        print(f"Admin user '{admin_email}' already exists, skipping...")
        return

    # Создание админа
    admin = User(
        email=admin_email,
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        full_name="Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print(f"✅ Created admin user: {admin_email}")
    print(f"   Password: {settings.FIRST_SUPERUSER_PASSWORD}")
    print("   ⚠️  IMPORTANT: Change this password in production!")


def init_db():
    """Инициализация базы данных"""
    print("🚀 Initializing database...")

    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

    # Получение сессии
    db = SessionLocal()

    try:
        # Инициализация категорий
        print("\n📁 Creating categories...")
        init_categories(db)

        # Инициализация администратора
        print("\n👤 Creating admin user...")
        init_admin(db)

        print("\n✨ Database initialization completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
