from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:senha@localhost/b3'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base =  declarative_base()

def db_insert(model):
    db = SessionLocal()
    db.add(model)
    db.commit()
    db.close()
