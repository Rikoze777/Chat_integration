from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Создаем базовый класс для моделей
Base = declarative_base()

# Класс User
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # Связь с таблицей Dataset
    datasets = relationship('Dataset', back_populates='user')

# Класс Dataset
class Dataset(Base):
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Связь с таблицей User
    user = relationship('User', back_populates='datasets')

# Создаем движок базы данных
engine = create_engine('sqlite:///mydatabase.db', echo=True)

# Создаем таблицы в базе данных
Base.metadata.create_all(engine)

# Создаем сессию для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Пример использования
if __name__ == '__main__':
    # Создаем пользователя
    new_user = User(username='mjdanny', email='mjdanny@example.com')
    session.add(new_user)
    session.commit()

    # Создаем набор данных для пользователя
    new_dataset = Dataset(name='Data', user_id=new_user.id)
    session.add(new_dataset)
    session.commit()

    # Выводим информацию о пользователе и его наборах данных
    user = session.query(User).filter_by(username='mjdanny').first()
    print(f"User: {user.username}, Email: {user.email}")
    for dataset in user.datasets:
        print(f"Dataset: {dataset.name}")