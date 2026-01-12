from datetime import datetime
from typing import Optional
from enum import Enum
import pytz
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg

# Setup Timezone Jakarta
jakarta_tz = pytz.timezone("Asia/Jakarta")

def get_jakarta_now():
    return datetime.now(jakarta_tz)

class UserType(str, Enum):
    BIASA = "biasa"
    CORPORATE = "corporate"
    ADMIN = "admin"

class User(SQLModel, table=True):
    __tablename__ = "users"  
    uuid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            unique=True,
            nullable=False
        )
    )

    # Identitas & Kredensial
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False) 
    role: UserType = Field(
        default=UserType.BIASA,
        sa_column=Column(pg.VARCHAR, nullable=False, default=UserType.BIASA.value)
    )
    is_active: bool = Field(default=True)

    # Audit (Timezone Aware)
    waktu_create: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False)
    )
    
    waktu_update: datetime = Field(
        default_factory=get_jakarta_now,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=get_jakarta_now
        )
    )