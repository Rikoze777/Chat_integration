import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker


load_dotenv()
database_url = os.getenv("DATABASE_URL")
engine = create_async_engine(database_url, echo=True, future=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
