from typing import Optional

import structlog
from clients.audio import AudioModifier
from clients.constants import BaseAudioModificationException, BaseFileException
from common.utils import cleanup_file, get_exception_message
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKey
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool
from typing_extensions import Annotated

from .auth import get_api_key

logger = structlog.get_logger()

router = APIRouter(
    prefix="/api/v1/audio",
    tags=["api"],
)


@router.post("/dbfs/", response_class=FileResponse)
async def modify_dbfs(
    upload_file: Annotated[
        UploadFile,
        File(alias="file", validation_alias="file"),
    ],
    target: Annotated[float, Form()],
    file_name: Annotated[
        Optional[str],
        Form(description="Not a required field with a file name to use"),
    ] = None,
    _: APIKey = Depends(get_api_key),
):
    """Modifing dBFS of an uploaded file to a target value."""
    file_name_ = file_name if file_name is not None else upload_file.filename
    if file_name_ is None:
        msg = "No file_name passed both as a form's field or with an uploaded file"
        await logger.ainfo(msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    try:
        audio_modifier = await run_in_threadpool(
            AudioModifier,
            audio=upload_file.file,
            file_name=file_name_,
        )
        await run_in_threadpool(audio_modifier.change_dbfs, target)
        tmp_file = await run_in_threadpool(audio_modifier.export)
    except BaseFileException as e:
        await logger.aexception(str(e), **e.metadata, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_exception_message(e),
        )
    except BaseAudioModificationException as e:
        await logger.aexception(str(e), **e.metadata, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_exception_message(e),
        )
    except Exception as e:
        await logger.aexception("Unexpected exception occured", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    cleanup_file_task = BackgroundTask(cleanup_file, tmp_file)
    return FileResponse(
        path=tmp_file.name,
        filename=file_name,
        background=cleanup_file_task,
    )
