from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from datetime import date


class NoteBaseSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, description="Note content")


class NoteCreateSchema(NoteBaseSchema):
    pass


class NoteUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, description="Note content")


class NoteResponseSchema(NoteBaseSchema):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteListResponseSchema(BaseModel):
    notes: list[NoteResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    
class NoteSearchSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Search in title (partial match, case-insensitive)")
    
    created_after: Optional[date] = Field(None, description="Filter notes created after this date (inclusive), format: YYYY-MM-DD"
    )
    created_before: Optional[date] = Field(None, description="Filter notes created before this date (inclusive), format: YYYY-MM-DD"
    )