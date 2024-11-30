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
    user = await get_user(chat_id, session)
    if user:
        return user
    new_user = models.User(tg_user_id=chat_id)
    session.add(new_user)
    await session.commit()


async def search_docs(query: str, chat_id, session: AsyncSession, top_k: int = 3):
    user = await get_user(chat_id, session)
    query_vector = embed_model.encode(query).tolist()

    result = await session.execute(
        """
        SELECT content, embedding <=> :query_vector AS distance
        FROM documents
        WHERE user_id = :id
        ORDER BY distance ASC
        LIMIT :top_k
        """,
        {"query_vector": query_vector, "id": user.id, "top_k": top_k}
     )
    
    return result.fetchall()


async def add_chunks_to_db(chat_id: int, chunks: list[str], embeddings: list[np.ndarray], session: AsyncSession):
    """Добавляет чанки и их эмбеддинги в базу данных."""
    user = await get_user(chat_id, session)
    for content, embedding in zip(chunks, embeddings):
        embedding_list = embedding.tolist()
        dataset = models.Dataset(content=content, embedding=embedding_list, user_id=user.id)
        session.add(dataset)
    await session.commit()


async def get_sql(chat_id: int, session: AsyncSession):
    user = await get_user(chat_id, session)
    statement = select(models.SqlData).where(models.SqlData.user_id == user.id)
    result = await session.execute(statement)
    sql = result.scalars().first()
    return sql


async def add_sql(chat_id: int, sql: str, session: AsyncSession):
    user = await get_user(chat_id, session)
    sql = models.SqlData(user_id=user.id, content=sql)
    session.add(sql)
    await session.commit()


async def load_prompt(session: AsyncSession, chat_id: int, prompt: str):
    user = await get_user(chat_id, session)
    result = models.Instruction(user_id=user.id, content=prompt)
    session.add(result)
    await session.commit()


async def fetch_prompt(session: AsyncSession, chat_id: int):
    user = await get_user(chat_id, session)
    statement = select(models.Instruction).where(models.Instruction.user_id == user.id)
    result = await session.execute(statement)
    prompt = result.scalars().first()
    return prompt
