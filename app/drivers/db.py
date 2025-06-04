from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def db_context():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def db_transaction(expunge_all=True,flush=True)->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session  
            if flush:
                await session.flush()
            if expunge_all:
                session.expunge_all()
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


@asynccontextmanager
async def db_readonly()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
