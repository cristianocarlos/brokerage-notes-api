from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class Token(BaseModel):
    access_token: str
    token_type: str

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail='Acesso não autorizado')
        return {'username': username, 'user_id': user_id}
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f'Erro na tentativa de autorização {e}')

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
 encode = {'sub': username, 'id': user_id}
 expires = int((datetime.now(timezone.utc) + expires_delta).timestamp())
 encode.update({'exp': expires})
 return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post('/token', response_model=Token)
async def login_token():
    token = create_access_token('admin', 1, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
