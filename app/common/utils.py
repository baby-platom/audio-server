import os
from typing import IO

from .constants import BaseExceptionWithMetadata


def get_exception_message(exception: BaseExceptionWithMetadata) -> str:
    return f"{str(exception)}\n metadata: {exception.metadata}"


def cleanup_file(file: IO):
    file.close()
    os.unlink(file.name)
