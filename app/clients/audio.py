from enum import Enum
from tempfile import NamedTemporaryFile, SpooledTemporaryFile
from typing import IO

import structlog
from pydub import AudioSegment

from .constants import FileExtensionExtractionException, FileExtensionIsNotSupportedException, PositiveDBFSException

logger = structlog.get_logger()


class SupportedAudioFormats(Enum):
    WAV = "wav"
    MP3 = "mp3"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class AudioModifier:
    def __init__(
        self,
        audio: SpooledTemporaryFile,
        file_name: str,
    ) -> None:
        """Client for modification of an audio data."""
        self.file_name = file_name
        self.extension = self.extract_file_extension()
        if self.extension is SupportedAudioFormats.WAV:
            self.audio: AudioSegment = AudioSegment.from_wav(audio)
        elif self.extension is SupportedAudioFormats.MP3:
            self.audio: AudioSegment = AudioSegment.from_mp3(audio)
        else:
            raise FileExtensionIsNotSupportedException(
                "File extensions is not supported",
                metadata={
                    "file_name": self.file_name,
                    "supported_audio_formats": [name.value for name in SupportedAudioFormats],
                },
            )

    def change_dbfs(self, target: float) -> None:
        """Change the dBFS of the downloaded file to the target value."""
        if target > 0:
            raise PositiveDBFSException(
                "dBFS value can not be possitive",
                metadata={"target": target},
            )

        initial_dBFS = self.audio.dBFS
        delta = target - initial_dBFS
        self.audio = self.audio.apply_gain(delta)
        logger.debug(
            "Changed dBFS",
            initial=initial_dBFS,
            result=self.audio.dBFS,
            file_name=self.file_name,
        )

    def export(self) -> IO:
        """Export modified file to a NamedTemporaryFile using self.extension as a suffix."""
        tmp_file = NamedTemporaryFile(suffix=f".{self.extension}", delete=False)
        self.audio.export(tmp_file, format=self.extension.value)
        return tmp_file

    def extract_file_extension(self) -> SupportedAudioFormats:
        parts = self.file_name.split(".")
        if len(parts) < 2:
            raise FileExtensionExtractionException(
                "File has no extension",
                metadata={"file_name": self.file_name},
            )

        extension = parts[-1]
        if SupportedAudioFormats.has_value(extension) is False:
            raise FileExtensionIsNotSupportedException(
                "File extensions is not supported",
                metadata={
                    "file_name": self.file_name,
                    "supported_audio_formats": [name.value for name in SupportedAudioFormats],
                },
            )

        return SupportedAudioFormats(extension)
