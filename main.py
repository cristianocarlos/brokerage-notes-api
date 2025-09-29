from fastapi import FastAPI
from models import Base
from database import engine
from routers import auth, common

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get('/healthy')
async def healthy_check():
    return {'message': 'Healthy'}

app.include_router(auth.router)
app.include_router(common.router)
