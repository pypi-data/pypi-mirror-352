from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    STATUS_OK: _ClassVar[Status]
    STATUS_ERROR: _ClassVar[Status]
STATUS_UNSPECIFIED: Status
STATUS_OK: Status
STATUS_ERROR: Status

class UnitTask(_message.Message):
    __slots__ = ("task_class_name", "task_config")
    TASK_CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    task_class_name: str
    task_config: str
    def __init__(self, task_class_name: _Optional[str] = ..., task_config: _Optional[str] = ...) -> None: ...
