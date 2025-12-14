from schemas.note_schemas import NoteCreateSchema, NoteUpdateSchema, NoteResponseSchema, NoteListResponseSchema, NoteSearchSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, Query
from sqlalchemy import select, update, delete, func, and_
from models.notes_models import Note
from uuid import UUID
from typing import Optional
from datetime import datetime



class NoteController:
    
    @staticmethod
    async def create_note_func(data: NoteCreateSchema, user_id: UUID, db: AsyncSession) -> NoteResponseSchema:
        try:
            new_note = Note(
                title=data.title,
                content=data.content,
                user_id=user_id
            )
            
            db.add(new_note)
            
            await db.commit()
            await db.refresh(new_note)
            
            return NoteResponseSchema.model_validate(new_note)
            
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database integrity error")
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error")
            
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error')
            )

    
    @staticmethod
    async def get_note_func(note_id: UUID, user_id: UUID, db: AsyncSession) -> NoteResponseSchema:
        try:
            statement = select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id,
                Note.is_deleted == False 
            )
            
            result = await db.execute(statement)
            
            note = result.scalar_one_or_none()
            
            if not note:
                raise HTTPException(status_code=404, detail="Note not found or you don't have permission to access it"
                )
            
            return NoteResponseSchema.model_validate(note)
            
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
        except Exception as e:
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error')
            )
    
    
    @staticmethod
    async def list_notes_func(user_id: UUID, db: AsyncSession, page: int = Query(1, ge=1, description="Page number"), page_size: int = Query(10, ge=1, le=100, description="Items per page"),
        search: Optional[str] = Query(None, description="Search in title and content")
    ) -> NoteListResponseSchema:
        try:
            query = select(Note).where(Note.user_id == user_id, Note.is_deleted == False)
            
            if search:
                search_filter = Note.title.ilike(f"%{search}%") | Note.content.ilike(f"%{search}%")
                query = query.where(search_filter)
            
            count_query = select(func.count()).select_from(Note).where(Note.user_id == user_id, Note.is_deleted == False)
            
            if search:
                count_query = count_query.where(search_filter)
            
            total_result = await db.execute(count_query)
            total = total_result.scalar_one()
            
            offset = (page - 1) * page_size
            
            total_pages = (total + page_size - 1) // page_size
            
            query = query.offset(offset).limit(page_size).order_by(Note.updated_at.desc())
            
            result = await db.execute(query)
            notes = result.scalars().all()
            
            return NoteListResponseSchema(
                notes=[NoteResponseSchema.model_validate(note) for note in notes],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error")
            
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error')
            )
            
    
    @staticmethod
    async def update_note_func(note_id: UUID, data: NoteUpdateSchema, user_id: UUID, db: AsyncSession) -> NoteResponseSchema:
        try:
            check_statement = select(Note).where(Note.id == note_id,
                Note.user_id == user_id)
            
            check_result = await db.execute(check_statement)
            
            existing_note = check_result.scalar_one_or_none()
            
            if not existing_note:
                raise HTTPException(status_code=404, detail="Note not found or you don't have permission to update it")
            
            update_data = {}
            
            if data.title is not None:
                update_data['title'] = data.title
                
            if data.content is not None:
                update_data['content'] = data.content
            
            update_statement = (update(Note).where(Note.id == note_id, Note.user_id == user_id).values(**update_data).execution_options(synchronize_session="fetch")
            )
            
            await db.execute(update_statement)
            await db.commit()
            
            await db.refresh(existing_note)
            
            return NoteResponseSchema.model_validate(existing_note)
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error")
            
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error')
            )
    
    
    @staticmethod
    async def soft_delete_note_func(note_id: UUID, user_id: UUID, db: AsyncSession) -> dict:
        try:
            check_statement = select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.is_deleted == False 
            )
            
            check_result = await db.execute(check_statement)
            
            existing_note = check_result.scalar_one_or_none()
            
            if not existing_note:
                raise HTTPException(status_code=404, detail="Note not found, already deleted, or you don't have permission to delete it")
            
            update_statement = (update(Note).where(Note.id == note_id, Note.user_id == user_id).values(is_deleted=True))
            
            await db.execute(update_statement)
            await db.commit()
            
            return {
                "message": "Note soft deleted successfully",
                "note_id": str(note_id),
                "deleted_at": datetime.now().isoformat()
            }
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error")
            
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error')
            )
            
            
    async def search_notes_func(user_id: UUID, filters: NoteSearchSchema, db: AsyncSession, page: int = 1, page_size: int = 10) -> NoteListResponseSchema:
        try:
            conditions = [
                Note.user_id == user_id,
                Note.is_deleted == False
            ]
            
            if filters.title and filters.title.strip():
                search_term = filters.title.strip()
                conditions.append(Note.title.ilike(f"%{search_term}%"))
            
            if filters.created_after:
                created_after_dt = datetime.combine(filters.created_after, datetime.min.time())
                conditions.append(Note.created_at >= created_after_dt)
            
            if filters.created_before:
                created_before_dt = datetime.combine(filters.created_before, datetime.max.time())
                
                conditions.append(Note.created_at <= created_before_dt)
            
            if filters.created_after and filters.created_before:
                if filters.created_after > filters.created_before:
                    raise HTTPException(status_code=400, detail="created_after date must be less than or equal to created_before date")
            
            query = select(Note).where(and_(*conditions))
            
            count_query = select(func.count()).select_from(Note).where(and_(*conditions))
            
            total_result = await db.execute(count_query)
            
            total = total_result.scalar_one()
            
            offset = (page - 1) * page_size
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
            
            query = query.order_by(Note.created_at.desc()).offset(offset).limit(page_size)
            
            result = await db.execute(query)
            
            notes = result.scalars().all()
            
            return NoteListResponseSchema(
                notes=[NoteResponseSchema.model_validate(note) for note in notes],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error!')
            )
            
            
    