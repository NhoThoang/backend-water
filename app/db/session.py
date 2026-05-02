from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Cấu hình Async Engine với Connection Pooling
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_size=10,        # Min connections in the pool
    max_overflow=20,     # Max additional connections when pool is full
    pool_pre_ping=True,  # Check connection health before use
    echo=False           # Set to True for SQL logging
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
