from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import BigInteger, Column
from pgvector.sqlalchemy import Vector


class BaseSQLModel(SQLModel, table=False):
    id: int = Field(primary_key=True)

    class Config:
        arbitrary_types_allowed = True


class User(BaseSQLModel, table=True):
    __tablename__ = 'user'

    tg_user_id: int = Field(
        title="Tg user id",
        description="User chat id from telegram",
        sa_column=Column(BigInteger)
    )
    profiles: list["Dataset"] = Relationship(back_populates="user")


class Dataset(BaseSQLModel, table=True):
    __tablename__ = 'dataset'

    content: str = Field(description="embedding content")
    embedding: Vector = Field(
        sa_column=Column(Vector(1024))
    )

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="datasets")


class SqlData(BaseSQLModel, table=True):
    __tablename__ ='sqldata'

    content: str = Field(description="embedding content")

    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="sqldatas")
