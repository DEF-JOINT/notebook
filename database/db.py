from database.passwords import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import UserModel
from database.models import TaskModel
from database.models import SubTaskModel


port = 5432
postgres_user = 'postgres'
password = '123'
db_name = 'postgres'

DATABASE_URL = f'postgresql+psycopg2://{postgres_user}:{password}@localhost:{port}/{db_name}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_all_users():
    database = SessionLocal()

    users = database.query(UserModel).all()

    database.close()

    return users


def get_user(username):
    database = SessionLocal()
    user = database.query(UserModel).filter(
        UserModel.username == username).first()
    database.close()

    return user


def create_user(username, password):
    database = SessionLocal()

    new_user = UserModel(
        username=username, password=get_password_hash(password))

    database.add(new_user)
    database.commit()
    database.close()

    return new_user


def get_user_tasks(user_id):
    database = SessionLocal()
    tasks = database.query(TaskModel).filter(
        TaskModel.user_id == user_id).all()
    database.close()

    return tasks


def create_task(user_id, name, description):
    database = SessionLocal()

    new_task = TaskModel(user_id=user_id, name=name, description=description)

    database.add(new_task)
    database.commit()
    database.close()

    return new_task


def delete_task_from_db(user_id, task_id):
    database = SessionLocal()

    task_to_delete = database.query(TaskModel).filter(
        TaskModel.user_id == user_id, TaskModel.id == task_id).one()
    database.delete(task_to_delete)
    database.commit()
    database.close()

    return task_to_delete.id


def get_user_task_subtasks(base_task_id, user_id):
    database = SessionLocal()
    subtasks = database.query(SubTaskModel).filter(
        SubTaskModel.base_task_id == base_task_id, SubTaskModel.user_id == user_id).all()
    database.close()

    return subtasks


def create_new_subtask(base_task_id, user_id, description):
    database = SessionLocal()

    new_task = SubTaskModel(base_task_id=base_task_id,
                            user_id=user_id, description=description)

    database.add(new_task)
    database.commit()
    database.close()

    return new_task


def delete_subtask_from_db(subtask_id, base_task_id, user_id):
    database = SessionLocal()

    subtask_to_delete = database.query(SubTaskModel).filter(
        SubTaskModel.user_id == user_id, SubTaskModel.id == subtask_id, SubTaskModel.base_task_id == base_task_id).one()

    database.delete(subtask_to_delete)
    database.commit()
    database.close()

    return None
