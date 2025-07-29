import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeployUnitTaskRequest(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: _common_pb2.UnitTask
    def __init__(self, task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ...) -> None: ...

class DeployUnitTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class TeardownUnitTaskRequest(_message.Message):
    __slots__ = ("task",)
    TASK_FIELD_NUMBER: _ClassVar[int]
    task: _common_pb2.UnitTask
    def __init__(self, task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ...) -> None: ...

class TeardownUnitTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class TaskManagerStatus(_message.Message):
    __slots__ = ("task", "status")
    TASK_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    task: _common_pb2.UnitTask
    status: _common_pb2.Status
    def __init__(self, task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ..., status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class HealthcheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthcheckResponse(_message.Message):
    __slots__ = ("status", "task_manager_statuses")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TASK_MANAGER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    task_manager_statuses: _containers.RepeatedCompositeFieldContainer[TaskManagerStatus]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., task_manager_statuses: _Optional[_Iterable[_Union[TaskManagerStatus, _Mapping]]] = ...) -> None: ...
