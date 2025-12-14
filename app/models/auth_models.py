from database.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID as u, uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Integer
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[u] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] =  mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    profile_pic: Mapped[str | None] = mapped_column(String, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, type={self.type})>"