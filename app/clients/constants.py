from common.constants import BaseExceptionWithMetadata


class BaseFileException(BaseExceptionWithMetadata):
    ...


class FileExtensionExtractionException(BaseFileException):
    ...


class FileExtensionIsNotSupportedException(BaseFileException):
    ...


class BaseAudioModificationException(BaseExceptionWithMetadata):
    ...


class PositiveDBFSException(BaseAudioModificationException):
    ...
