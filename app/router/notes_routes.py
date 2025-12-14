from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import date
from database.db import connect_db
from schemas.note_schemas import (
    NoteCreateSchema, 
    NoteUpdateSchema, 
    NoteResponseSchema, 
    NoteListResponseSchema,
    NoteSearchSchema
)
from middleware.auth_middleware import verify_authentication
from controllers.notes_controllers import NoteController
from dependencies.rate_limit import rate_limit_20_per_minute


note_router = APIRouter(
    prefix='/api/notes',
    tags=['Notes']
)


@note_router.get('/search', response_model=NoteListResponseSchema)
async def search_notes_route(
    request: Request,
    _ = Depends(rate_limit_20_per_minute),
    title: Optional[str] = Query(
        None, 
        min_length=1,
        description="Search in title (partial match, case-insensitive)"
    ),
    created_after: Optional[date] = Query(
        None,
        description="Filter notes created after this date (inclusive), format: YYYY-MM-DD"
    ),
    created_before: Optional[date] = Query(
        None,
        description="Filter notes created before this date (inclusive), format: YYYY-MM-DD"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(connect_db),
    payload: dict = Depends(verify_authentication)
):
    """
    Search notes by:
    - Title (partial match, case-insensitive)
    - Created date range
    
    Both parameters are optional. Use one or both.
    Returns paginated results.
    """
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    if not title and not created_after and not created_before:
        raise HTTPException(
            status_code=400,
            detail="At least one search parameter must be provided (title, created_after, or created_before)"
        )
    
    filters = NoteSearchSchema(
        title=title,
        created_after=created_after,
        created_before=created_before
    )
    
    return await NoteController.search_notes_func(
        user_id=UUID(user_id),
        filters=filters,
        db=db,
        page=page,
        page_size=page_size
    )
    

@note_router.post('', response_model=NoteResponseSchema, status_code=201)
async def create_note_route(request: Request, data: NoteCreateSchema, _ = Depends(rate_limit_20_per_minute),db: AsyncSession = Depends(connect_db), payload: dict = Depends(verify_authentication)):
    """
    Create a new note.
    
    - Requires authentication
    - Returns the created note
    """
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return await NoteController.create_note_func(data, UUID(user_id), db)


@note_router.get('/{note_id}', response_model=NoteResponseSchema)
async def get_note_route(request: Request, note_id: UUID, _ = Depends(rate_limit_20_per_minute), db: AsyncSession = Depends(connect_db), payload: dict = Depends(verify_authentication)):
    """
    Retrieve a single note by ID.
    
    - Requires authentication
    - User can only access their own notes
    """
    user_id = payload.get('id')
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return await NoteController.get_note_func(note_id, UUID(user_id), db)


@note_router.get('', response_model=NoteListResponseSchema)
async def list_notes_route(request: Request, _ = Depends(rate_limit_20_per_minute),     page: int = Query(1, ge=1, description="Page number"), page_size: int = Query(10, ge=1, le=100, description="Items per page"), search: Optional[str] = Query(None, description="Search in title and content"), db: AsyncSession = Depends(connect_db), payload: dict = Depends(verify_authentication)):
    """
    List all notes for the authenticated user.
    
    - Requires authentication
    - Supports pagination
    - Supports search by title/content
    - Returns only user's own notes
    """
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return await NoteController.list_notes_func(
        UUID(user_id), 
        db, 
        page, 
        page_size, 
        search
    )


@note_router.put('/{note_id}', response_model=NoteResponseSchema)
async def update_note_route(request: Request, note_id: UUID, data: NoteUpdateSchema, _ = Depends(rate_limit_20_per_minute), db: AsyncSession = Depends(connect_db), payload: dict = Depends(verify_authentication)):
    """
    Update an existing note.
    
    - Requires authentication
    - User can only update their own notes
    - Partial updates allowed
    """
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return await NoteController.update_note_func(note_id, data, UUID(user_id), db)


@note_router.delete('/{note_id}')
async def delete_note_route(request: Request, note_id: UUID, _ = Depends(rate_limit_20_per_minute), db: AsyncSession = Depends(connect_db), payload: dict = Depends(verify_authentication)):
    """
    Soft delete a note.
    
    - Requires authentication
    - User can only delete their own notes
    - Returns confirmation message
    """
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    return await NoteController.soft_delete_note_func(note_id, UUID(user_id), db)