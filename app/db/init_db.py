from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.tariff import Tariff
from app.models.customer import CustomerType
from app.db.base import Base
from app.db.session import engine
from app.utils.logger import logger

async def init_db(db: AsyncSession) -> None:
    # 1. Tạo các bảng nếu chưa có (Sử dụng run_sync cho Metadata)
    logger.info("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Tạo Admin mặc định
    stmt = select(User).where(User.username == settings.FIRST_SUPERUSER)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        logger.info(f"Creating superuser: {settings.FIRST_SUPERUSER}")
        user = User(
            username=settings.FIRST_SUPERUSER,
            password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            role=UserRole.ADMIN,
            password_set=1
        )
        db.add(user)
        await db.commit()
    else:
        logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER}")

    # 3. Seed Tariffs mẫu (Bậc thang)
    count_stmt = select(func.count()).select_from(Tariff)
    count_result = await db.execute(count_stmt)
    tariff_count = count_result.scalar()
    
    if tariff_count == 0:
        logger.info("Seeding initial tariffs...")
        # Bậc thang cho hộ sinh hoạt
        tariffs = [
            Tariff(customer_type=CustomerType.RESIDENTIAL, step_number=1, from_m3=0, to_m3=10, price_per_m3=6000),
            Tariff(customer_type=CustomerType.RESIDENTIAL, step_number=2, from_m3=10, to_m3=20, price_per_m3=8000),
            Tariff(customer_type=CustomerType.RESIDENTIAL, step_number=3, from_m3=20, to_m3=30, price_per_m3=10000),
            Tariff(customer_type=CustomerType.RESIDENTIAL, step_number=4, from_m3=30, to_m3=None, price_per_m3=15000),
            # Bậc thang cho kinh doanh (thường 1 giá cao)
            Tariff(customer_type=CustomerType.BUSINESS, step_number=1, from_m3=0, to_m3=None, price_per_m3=12000),
        ]
        db.add_all(tariffs)
        await db.commit()
    else:
        logger.info("Tariffs already exist, skipping seed.")
