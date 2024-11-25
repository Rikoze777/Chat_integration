import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any
from sqlalchemy import text
from collections.abc import AsyncGenerator
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
# async def get_session() -> AsyncGenerator[AsyncSession, Any]:
#     async_session_factory = async_sessionmaker(
#         bind=engine,
#         autoflush=False,
#         autocommit=False,
#         expire_on_commit=False,
#         class_=AsyncSession,
#     )
#     async with async_session_factory() as db_session:
#         await db_session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
#         try:
#             yield db_session
#         except SQLAlchemyError as err:
#             await db_session.rollback()
