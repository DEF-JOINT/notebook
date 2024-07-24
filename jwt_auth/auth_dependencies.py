from schemas import User
from jwt_auth.schemas import TokenData
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
import jwt
from jwt.exceptions import InvalidTokenError
from jwt_auth.authentification import get_user
import os
from schemas import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1.0/users/login")


async def get_current_user(token = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось авторизировать",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=[os.environ['ALGORITHM']])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
    
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(token_data.username)
    
    if user is None:
        raise credentials_exception
    
    return User(**user.__dict__)
