from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.config import env
from typing import AsyncGenerator


async_engine = create_async_engine(env.DB_URL, future=True,
                                    pool_size = env.DB_POOL_SIZE ,
                                    max_overflow = env.DB_MAX_OVERFLOW,
                                    pool_timeout = 30,
                                    pool_recycle = 1800,
                                    pool_pre_ping = True,
                                    echo=env.DB_ECHO
                                    )

AsyncSessionLocal = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def async_session(expunge_all=True,flush=True)-> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        if flush:
            await session.flush()
        if expunge_all:
            session.expunge_all()

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
            raise


@asynccontextmanager
async def db_readonly()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_if_not_exists():
    from urllib.parse import urlparse
    from sqlalchemy import text
    url = urlparse(env.DB_URL)
    db = url.path.lstrip('/')
    # no transaction
    engine = create_async_engine(url._replace(path='').geturl() , echo=True, future=True)
    # create db if not exists
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": db}
        )
        exists = result.scalar()
        if not exists:
            async with engine.connect() as conn1:
                sql = text(f'CREATE DATABASE "{db}"')
                await conn1.execution_options(isolation_level="AUTOCOMMIT")
                await conn1.execute(sql)
        else:
            print(f"Database {db} already exists")
    await engine.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_if_not_exists())