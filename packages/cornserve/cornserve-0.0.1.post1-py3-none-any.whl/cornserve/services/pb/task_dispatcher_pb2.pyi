import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskManagerDeployment(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class NotifyUnitTaskDeploymentRequest(_message.Message):
    __slots__ = ("task", "task_manager")
    TASK_FIELD_NUMBER: _ClassVar[int]
    TASK_MANAGER_FIELD_NUMBER: _ClassVar[int]
    task: _common_pb2.UnitTask
    task_manager: TaskManagerDeployment
    def __init__(self, task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ..., task_manager: _Optional[_Union[TaskManagerDeployment, _Mapping]] = ...) -> None: ...

class NotifyUnitTaskDeploymentResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class NotifyUnitTaskTeardownRequest(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: _common_pb2.UnitTask
    def __init__(self, task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ...) -> None: ...

class NotifyUnitTaskTeardownResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...
