from fastapi import FastAPI
from models import Base
from database import engine
from routers import auth, common
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://127.0.0.1:8004",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get('/healthy')
async def healthy_check():
    return {'message': 'Healthy'}

app.include_router(auth.router)
app.include_router(common.router)
