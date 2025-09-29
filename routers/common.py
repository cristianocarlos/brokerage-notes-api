from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()
from .auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/upload')
async def upload(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Endpoint não autorizado')
    return {'message': 'ok'}
