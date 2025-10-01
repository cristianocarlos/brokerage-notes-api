from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class TokenResponse(BaseModel):
    access_token: str
    expire_datetime: datetime

class TokenRequest(BaseModel):
    secret_key: str

def is_valid_secret_key(secret_key: str):
    return secret_key == SECRET_KEY

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

def create_access_token(username: str, user_id: int, secret_key: str, expire_datetime: datetime):
    encode = {'sub': username, 'id': user_id}
    encode.update({'exp': int(expire_datetime.timestamp())})
    return jwt.encode(encode, secret_key, algorithm=ALGORITHM)

@router.post('/token', response_model=TokenResponse)
async def login_token(request: TokenRequest):
    if not is_valid_secret_key(request.secret_key):
        raise HTTPException(status_code=401, detail='Secret key inválida')
    expire_datetime = datetime.now(timezone.utc) + timedelta(minutes=20)
    token = create_access_token('admin', 1, request.secret_key, expire_datetime)
    return {'access_token': token, 'expire_datetime': expire_datetime}
