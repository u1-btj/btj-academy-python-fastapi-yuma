from pydantic import BaseModel, Field
from api.base.base_schemas import BaseResponse, PaginationParams, PaginationMetaResponse

from models.note import NoteSchema

class AddNoteRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=500)

class AddNoteResponse(BaseResponse):
    data: NoteSchema | None

class UpdateNoteRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=500)

class UpdateNoteResponse(BaseResponse):
    data: NoteSchema | None

class GetNoteResponse(BaseResponse):
    data: NoteSchema | None

class NotePaginationResponse(BaseModel):
    records: list[NoteSchema]
    meta: PaginationMetaResponse
    
class GetAllNotesResponse(BaseResponse):
    data: NotePaginationResponse

class GetAllNotesRequest(PaginationParams):
    filter_by_user_id: bool = True
    include_deleted_note: bool = False