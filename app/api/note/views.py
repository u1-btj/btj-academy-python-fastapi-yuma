from fastapi import APIRouter, Depends, Path, Request, Response, HTTPException
from api.base.base_schemas import BaseResponse, PaginationParams
from middlewares.authentication import get_user_id_from_access_token

from .schemas import (
    AddNoteRequest,
    AddNoteResponse,
    UpdateNoteRequest,
    UpdateNoteResponse,
    GetNoteResponse,
    GetAllNotesRequest,
    GetAllNotesResponse,
    NotePaginationResponse
)
from .use_cases import (
    AddNewNote,
    DeleteNote,
    UpdateNote,
    GetNote,
    GetAllNotes
)

router = APIRouter(prefix="/notes")
tag = "Notes"

@router.post("", response_model=AddNoteResponse, tags=[tag])
async def add_new_note(
    response: Response,
    body: AddNoteRequest,
    user_id: int = Depends(get_user_id_from_access_token),
    add_note: AddNewNote = Depends(AddNewNote)
) -> AddNoteResponse:
    try:
        resp_data = await add_note.execute(request=body, user_id=user_id)

        return AddNoteResponse(
            status="success",
            message="success add new note",
            data=resp_data
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return AddNoteResponse(
            status="error",
            message=ex.detail
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to add new note"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return AddNoteResponse(
            status="error",
            message=message
        )

@router.delete("/{note_id}", response_model=BaseResponse, tags=[tag])
async def delete_note(
    response: Response,
    note_id: int = Path(..., description=""),
    user_id: int = Depends(get_user_id_from_access_token),
    delete: DeleteNote = Depends(DeleteNote)
) -> BaseResponse:
    try:
        await delete.execute(user_id=user_id, note_id=note_id)
        return BaseResponse(
            status="success",
            message="success delete note"
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return BaseResponse(
            status="error",
            message=ex.detail
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to delete note"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return BaseResponse(
            status="error",
            message=message
        )
    
@router.put("/{note_id}", response_model=UpdateNoteResponse, tags=[tag])
async def update_note(
    response: Response,
    body: UpdateNoteRequest,
    note_id: int = Path(..., description=""),
    user_id: int = Depends(get_user_id_from_access_token),
    update: UpdateNote = Depends(UpdateNote),
) -> UpdateNoteResponse:
    try:
        resp_data = await update.execute(request=body, user_id=user_id, note_id=note_id)

        return UpdateNoteResponse(
            status="success",
            message="success update note",
            data=resp_data
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return UpdateNoteResponse(
            status="error",
            message=ex.detail
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to update note"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return UpdateNoteResponse(
            status="error",
            message=message
        )

@router.get("/{note_id}", response_model=GetNoteResponse, tags=[tag])
async def get_note(
    response: Response,
    note_id: int = Path(..., description=""),
    user_id: int = Depends(get_user_id_from_access_token),
    get_note: GetNote = Depends(GetNote),
) -> GetNoteResponse:
    try:
        resp_data = await get_note.execute(user_id=user_id, note_id=note_id)

        return GetNoteResponse(
            status="success",
            message="success get note",
            data=resp_data
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return GetNoteResponse(
            status="error",
            message=ex.detail
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to get note"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return GetNoteResponse(
            status="error",
            message=message
        )

@router.get("", response_model=GetAllNotesResponse, tags=[tag])
async def get_all_notes(
    response: Response,
    user_id: int = Depends(get_user_id_from_access_token),
    page_params: GetAllNotesRequest = Depends(),
    get_all: GetAllNotes = Depends(GetAllNotes),
) -> GetAllNotesResponse:
    try:
        resp_data = await get_all.execute(
            page_params=page_params, user_id=user_id
        )

        return GetAllNotesResponse(
            status="success",
            message="success get all notes",
            data=NotePaginationResponse(records=resp_data[0], meta=resp_data[1])
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return GetAllNotesResponse(
            status="error",
            message=ex.detail
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to get all notes"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return GetAllNotesResponse(
            status="error",
            message=message
        )
