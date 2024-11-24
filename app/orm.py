import numpy as np
from sqlalchemy import select
import models
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer


embed_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


async def get_user(chat_id: int, session: AsyncSession) -> models.User:
    statement = select(models.User).where(models.User.tg_user_id == chat_id)
    result = await session.execute(statement)
    user = result.scalars().first()
    return user


async def create_user(chat_id: int, session: AsyncSession) -> models.User | None:
    user = get_user(chat_id, session)
    if user:
        return user
    new_user = models.User(tg_user_id=chat_id)
    session.add(new_user)
    await session.commit()


async def search_docs(query: str, session: AsyncSession, top_k: int = 5):
    query_vector = embed_model.encode(query).tolist()

    result = await session.execute(
        """
        SELECT content, embedding <=> :query_vector AS distance
        FROM documents
        ORDER BY distance ASC
        LIMIT :top_k
        """,
        {"query_vector": query_vector, "top_k": top_k}
    )
    
    return result.fetchall()


async def add_embeddings(user_id: int, content: str, embedding: np.ndarray, session: AsyncSession):
    embedding_list = embedding.tolist()
    dataset = models.Dataset(content=content, embedding=embedding_list, user_id=user_id)
    session.add(dataset)
    await session.commit()


async def get_sql(chat_id: int, session: AsyncSession):
    statement = select(models.SqlData).where(models.SqlData.user_id == chat_id)
    result = await session.execute(statement)
    user = result.scalars().first()
    return user
