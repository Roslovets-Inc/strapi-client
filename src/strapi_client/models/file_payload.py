from typing import Self
from pathlib import Path
from io import BytesIO
import mimetypes
from pydantic import BaseModel


class FilePayload(BaseModel, arbitrary_types_allowed=True):
    name: str
    file: BytesIO
    mimetype: str

    @classmethod
    def from_path(cls, file_path: Path | str) -> Self:
        fp = Path(file_path)
        return cls(name=fp.name, file=BytesIO(fp.read_bytes()), mimetype=cls._get_mimetype(fp.name))

    @classmethod
    def from_bytes(cls, file_name: str, file_bytes: BytesIO) -> Self:
        file_bytes.seek(0)
        return cls(name=file_name, file=file_bytes, mimetype=cls._get_mimetype(file_name))

    @classmethod
    def list_from_files(cls, files: list[Path | str] | dict[str, BytesIO]) -> list[Self]:
        file_payloads: list[Self] = []
        if isinstance(files, list):
            for file_path in files:
                file_payloads.append(cls.from_path(file_path=file_path))
        elif isinstance(files, dict):
            for file_name, file_bytes in files.items():
                file_payloads.append(cls.from_bytes(file_name=file_name, file_bytes=file_bytes))
        else:
            raise ValueError("Files must be a list of paths or a dict of file name and file data.")
        return file_payloads

    def to_files_tuple(self) -> tuple[str, tuple[str, BytesIO, str]]:
        return "files", (self.name, self.file, self.mimetype)

    @staticmethod
    def _get_mimetype(file_path: str) -> str:
        mimetype, _ = mimetypes.guess_type(file_path)
        return mimetype or "application/octet-stream"
