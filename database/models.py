from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from datetime import datetime
from typing import List


Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String, index=True)
    password = mapped_column(String)

    created_at = mapped_column(DateTime, default=datetime.now)


class SubTaskModel(Base):
    __tablename__ = 'subtasks'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id = mapped_column(Integer, index=True, nullable=False)
    description = mapped_column(String)

    base_task_id = mapped_column(ForeignKey('tasks.id'))


class TaskModel(Base):
    __tablename__ = 'tasks'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id = mapped_column(Integer, index=True, nullable=False)
    name = mapped_column(String, index=True)
    description = mapped_column(String)

    sub_items: Mapped[List[SubTaskModel]] = relationship()


if __name__ == '__main__':
    from sqlalchemy import create_engine

    DATABASE_URL = 'postgresql+psycopg2://postgres:123@localhost:5432/postgres'
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

    print('Database Initialized')
