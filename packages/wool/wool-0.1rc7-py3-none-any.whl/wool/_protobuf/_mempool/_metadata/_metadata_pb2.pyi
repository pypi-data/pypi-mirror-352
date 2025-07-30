from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class _MetadataMessage(_message.Message):
    __slots__ = ("ref", "mutable", "size", "md5")
    REF_FIELD_NUMBER: _ClassVar[int]
    MUTABLE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MD5_FIELD_NUMBER: _ClassVar[int]
    ref: str
    mutable: bool
    size: int
    md5: bytes
    def __init__(self, ref: _Optional[str] = ..., mutable: bool = ..., size: _Optional[int] = ..., md5: _Optional[bytes] = ...) -> None: ...
