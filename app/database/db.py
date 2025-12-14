from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import HTTPException
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv # type: ignore


load_dotenv()


database_url = os.getenv('POSTGRES_DATABASE_URL')

if not database_url:
    raise ValueError("POSTGRES_DATABASE_URL is not set in .env file")

engine = create_async_engine(database_url)

Base = declarative_base()

SessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)


async def connect_db() -> AsyncSession: # type: ignore
    async with SessionLocal() as session:
        try:
            yield session
            
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail='Database connection failed!')