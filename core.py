from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from jwt_auth.authentification import authenticate_user
from jwt_auth.jwt_base import create_access_token
from jwt_auth.auth_dependencies import get_current_user
from jwt_auth.schemas import Token

from schemas import User
from schemas import UserCreate
from schemas import TaskValidator
from schemas import TaskDeletion
from schemas import SubtaskCreate
from schemas import SubtaskDelete
from database.db import create_user
from database.db import get_user_tasks
from database.db import create_task
from database.db import delete_task_from_db
from database.db import get_user_task_subtasks
from database.db import create_new_subtask
from database.db import delete_subtask_from_db
import os

from telebot import TeleBot

os.environ['SECRET_KEY'] = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
os.environ['ALGORITHM'] = "HS256"
os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'

os.environ['TELEGRAM_BOT_TOKEN'] = '6488136875:AAHB-aYD0VEiaYUE1YVzXyuWiKYT1iBK7U8'

bot = TeleBot(os.environ['TELEGRAM_BOT_TOKEN'])

kernel = FastAPI()

allowed = [
    'http://127.0.0.1'
]

kernel.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --- USERS ---

@kernel.post('/api/v1.0/users/create')
async def create(user_data: UserCreate):
    new_user = create_user(user_data.username, user_data.password)

    bot.send_message(-4, f'Создан новый пользователь под  логином {user_data.username}!')

    return new_user


@kernel.post("/api/v1.0/users/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)) -> Token:
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(
        os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']))

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@kernel.post("/api/v1.0/users/current_user")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


# --- TASKS ---

@kernel.get("/api/v1.0/tasks/get_tasks_by_current_user/")
async def read_own_items(current_user: User = Depends(get_current_user)):
    user_id = current_user.id

    tasks = get_user_tasks(user_id)

    return tasks


@kernel.post('/api/v1.0/tasks/create_new')
async def add_new_task(task: TaskValidator, current_user: User = Depends(get_current_user)) -> int:
    '''
    Create new task
    '''

    tasks = get_user_tasks(current_user.id)
    if len(tasks) >= 5 and current_user.role == 'standard':
        raise HTTPException(403, 'Too much tasks')
    if len(tasks) >= 10 and current_user.role == 'premium':
        raise HTTPException(403, 'Too much tasks')

    new_task = create_task(current_user.id, task.name, task.description)

    return new_task.id


@kernel.delete('/api/v1.0/tasks/delete_by_uid')
async def delete_task(task_id: TaskDeletion, current_user: User = Depends(get_current_user)):
    subtasks = get_user_task_subtasks(task_id.id, current_user.id)
    for subtask in subtasks:
        delete_subtask_from_db(subtask.id, task_id.id, current_user.id)

    delete_task_from_db(current_user.id, task_id.id)

    return None


# --- SUBTASKS ---

@kernel.post("/api/v1.0/subtasks/get_subtasks_by_task_id")
async def read_own_items(base_task_id: int, current_user: User = Depends(get_current_user)):
    subtasks = get_user_task_subtasks(base_task_id, current_user.id)

    return subtasks


@kernel.post("/api/v1.0/subtasks/create_new_subtask")
async def add_new_subtask(subtask_data: SubtaskCreate, current_user: User = Depends(get_current_user)) -> int:
    subtasks = get_user_task_subtasks(subtask_data.base_task_id, current_user.id)

    if len(subtasks) >= 3 and current_user.role == 'standard':
        raise HTTPException(403, 'Too much subtasks')
    
    new_subtask = create_new_subtask(
        subtask_data.base_task_id, current_user.id, subtask_data.description)

    return new_subtask.id


@kernel.post("/api/v1.0/subtasks/delete_subtask")
async def delete_subtask(subtask_data: SubtaskDelete, current_user: User = Depends(get_current_user)):
    delete_subtask_from_db(subtask_data.subtask_id,
                           subtask_data.base_task_id, current_user.id)

    return None
