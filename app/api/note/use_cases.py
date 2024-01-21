import datetime
import math
from typing import Annotated

from fastapi import Depends, HTTPException

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from db import get_session
from api.base.base_schemas import PaginationMetaResponse, PaginationParams
from models.note import Note, NoteSchema
from .schemas import AddNoteRequest, UpdateNoteRequest, GetAllNotesRequest

AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]

class AddNewNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, request: AddNoteRequest, user_id: int) -> NoteSchema:
        async with self.async_session.begin() as session:
            note = Note()
            note.title = request.title
            note.content = request.content
            note.created_by = user_id
            note.updated_by = user_id
            note.created_at = datetime.datetime.utcnow()
            note.updated_at = datetime.datetime.utcnow()

            session.add(note)
            await session.flush()

            return NoteSchema.from_orm(note)

class DeleteNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int, note_id: int) -> NoteSchema:
        async with self.async_session.begin() as session:
            note = await session.execute(
                select(Note).where(
                    (Note.note_id == note_id).__and__(Note.deleted_at == None)
                )
            )
            note = note.scalars().first()

            if not note:
                raise HTTPException(status_code=404, detail="note not found")

            if note.created_by != user_id:
                raise HTTPException(status_code=401, detail="not valid credentials")

            note.deleted_at = datetime.datetime.utcnow()
            note.deleted_by = user_id

            await session.flush()

            return NoteSchema.from_orm(note)

class UpdateNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, request: UpdateNoteRequest, user_id: int, note_id: int) -> NoteSchema:
        async with self.async_session.begin() as session:
            note = await session.execute(
                select(Note).where(
                    (Note.note_id == note_id).__and__(Note.deleted_at == None)
                )
            )
            note = note.scalars().first()

            if not note:
                raise HTTPException(status_code=404, detail="note not found")
            
            if note.created_by != user_id:
                raise HTTPException(status_code=401, detail="not valid credentials")

            note.title = request.title
            note.content = request.content
            note.updated_at = datetime.datetime.utcnow()
            note.updated_by = user_id

            await session.flush()

            return NoteSchema.from_orm(note)
        
class GetNote:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int, note_id: int) -> NoteSchema:
        async with self.async_session() as session:
            note = await session.execute(
                select(Note).where(
                    (Note.note_id == note_id).__and__(Note.deleted_at == None)
                )
            )
            note = note.scalars().first()

            if not note:
                raise HTTPException(status_code=404, detail="note not found")
            
            if note.created_by != user_id:
                raise HTTPException(status_code=401, detail="not valid credentials")

            return NoteSchema.from_orm(note)

class GetAllNotes:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        page_params: GetAllNotesRequest,
        user_id: int
    ) -> (list[NoteSchema], PaginationMetaResponse):
        async with self.async_session() as session:
            page_query = (
                select(Note)
                .offset((page_params.page - 1) * page_params.item_per_page)
                .limit(page_params.item_per_page)
            )

            total_query = (
                select(func.count())
                .select_from(Note)
            )

            if page_params.filter_by_user_id:
                page_query = page_query.filter(Note.created_by == user_id)
                total_query = total_query.filter(Note.created_by == user_id)
            
            if not page_params.include_deleted_note:
                page_query = page_query.filter(Note.deleted_at == None)
                total_query = total_query.filter(Note.deleted_at == None)

            paginated_query = await session.execute(page_query)
            paginated_query = paginated_query.scalars().all()
            
            total_item = await session.execute(total_query)
            total_item = total_item.scalar()

            notes = [NoteSchema.from_orm(p) for p in paginated_query]

            meta = PaginationMetaResponse(
                total_item=total_item,
                page=page_params.page,
                item_per_page=page_params.item_per_page,
                total_page=math.ceil(total_item / page_params.item_per_page),
            )

            return notes, meta
        