from passlib.context import CryptContext
from database.db import get_user


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = get_user(username)

    if user is None:
        return False

    if not verify_password(password, user.password):
        return False

    return user
