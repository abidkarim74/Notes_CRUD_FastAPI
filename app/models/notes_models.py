from app.database.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from uuid import UUID as u, uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Text, DateTime
from sqlalchemy.sql import func


class Note(Base):
    __tablename__ = 'notes'
    
    id: Mapped[u] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    user_id: Mapped[u] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False,
        index=True  
    )
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', user_id={self.user_id})>"