import os
from typing import Annotated
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from contextlib import asynccontextmanager
from .auth import get_current_user

UPLOAD_DIRECTORY = "uploaded_files"

@asynccontextmanager
async def lifespan(r: APIRouter):
    print("Application startup: Initializing resources...")
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    yield  # Application is running and serving requests
    print("Application shutdown: Cleaning up resources...")

router = APIRouter(lifespan=lifespan)

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/upload-directory')
async def upload_directory(user: user_dependency, files: List[UploadFile] = File(...)):
    if user is None:
        raise HTTPException(status_code=401, detail='Endpoint não autorizado')
    uploaded_filenames = []
    for file in files:
        if not file.filename: continue
        file_upload_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_upload_path, "wb") as buffer:
            buffer.write(await file.read())
        uploaded_filenames.append(file.filename)
    return {"message": "Directory uploaded successfully", "filenames": uploaded_filenames}
