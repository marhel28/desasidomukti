from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from config import Config
from sqlmodel import SQLModel


dB_engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,  
    pool_pre_ping=True,
    pool_size=100,          
    max_overflow=200,      
    pool_recycle=1800,      
    pool_timeout=60,        
    connect_args={
        "statement_cache_size": 1000,
    },
)
 
db_session_maker = async_sessionmaker(
    dB_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,   
)
 

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_session_maker() as session:
        yield session


async def init_db():
    async with dB_engine.begin() as conn:  
        from auth.model import User
        await conn.run_sync(SQLModel.metadata.create_all)

