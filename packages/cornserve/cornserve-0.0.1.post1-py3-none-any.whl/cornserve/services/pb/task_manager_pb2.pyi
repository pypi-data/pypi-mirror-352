import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResourceAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ADD: _ClassVar[ResourceAction]
    REMOVE: _ClassVar[ResourceAction]
ADD: ResourceAction
REMOVE: ResourceAction

class GPUResource(_message.Message):
    __slots__ = ("action", "node_id", "global_rank", "local_rank")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_RANK_FIELD_NUMBER: _ClassVar[int]
    LOCAL_RANK_FIELD_NUMBER: _ClassVar[int]
    action: ResourceAction
    node_id: str
    global_rank: int
    local_rank: int
    def __init__(self, action: _Optional[_Union[ResourceAction, str]] = ..., node_id: _Optional[str] = ..., global_rank: _Optional[int] = ..., local_rank: _Optional[int] = ...) -> None: ...

class RegisterTaskRequest(_message.Message):
    __slots__ = ("task_manager_id", "task", "gpus")
    TASK_MANAGER_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    task_manager_id: str
    task: _common_pb2.UnitTask
    gpus: _containers.RepeatedCompositeFieldContainer[GPUResource]
    def __init__(self, task_manager_id: _Optional[str] = ..., task: _Optional[_Union[_common_pb2.UnitTask, _Mapping]] = ..., gpus: _Optional[_Iterable[_Union[GPUResource, _Mapping]]] = ...) -> None: ...

class RegisterTaskResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class UpdateResourcesRequest(_message.Message):
    __slots__ = ("task_manager_id", "gpus")
    TASK_MANAGER_ID_FIELD_NUMBER: _ClassVar[int]
    GPUS_FIELD_NUMBER: _ClassVar[int]
    task_manager_id: str
    gpus: _containers.RepeatedCompositeFieldContainer[GPUResource]
    def __init__(self, task_manager_id: _Optional[str] = ..., gpus: _Optional[_Iterable[_Union[GPUResource, _Mapping]]] = ...) -> None: ...

class UpdateResourcesResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class ShutdownRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ShutdownResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class ReconcileTargetLoadRequest(_message.Message):
    __slots__ = ("task_id", "target_load")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_LOAD_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    target_load: float
    def __init__(self, task_id: _Optional[str] = ..., target_load: _Optional[float] = ...) -> None: ...

class ReconcileTargetLoadResponse(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    message: str
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., message: _Optional[str] = ...) -> None: ...

class ProfilePoint(_message.Message):
    __slots__ = ("num_gpus", "max_sustainable_load", "deployment_config")
    NUM_GPUS_FIELD_NUMBER: _ClassVar[int]
    MAX_SUSTAINABLE_LOAD_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    num_gpus: int
    max_sustainable_load: float
    deployment_config: DeploymentConfig
    def __init__(self, num_gpus: _Optional[int] = ..., max_sustainable_load: _Optional[float] = ..., deployment_config: _Optional[_Union[DeploymentConfig, _Mapping]] = ...) -> None: ...

class DeploymentConfig(_message.Message):
    __slots__ = ("num_replicas", "tensor_parallel_degree", "pipeline_parallel_degree", "gpu_assignments")
    NUM_REPLICAS_FIELD_NUMBER: _ClassVar[int]
    TENSOR_PARALLEL_DEGREE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_PARALLEL_DEGREE_FIELD_NUMBER: _ClassVar[int]
    GPU_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    num_replicas: int
    tensor_parallel_degree: int
    pipeline_parallel_degree: int
    gpu_assignments: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, num_replicas: _Optional[int] = ..., tensor_parallel_degree: _Optional[int] = ..., pipeline_parallel_degree: _Optional[int] = ..., gpu_assignments: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTaskProfileRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetTaskProfileResponse(_message.Message):
    __slots__ = ("profile_points",)
    PROFILE_POINTS_FIELD_NUMBER: _ClassVar[int]
    profile_points: _containers.RepeatedCompositeFieldContainer[ProfilePoint]
    def __init__(self, profile_points: _Optional[_Iterable[_Union[ProfilePoint, _Mapping]]] = ...) -> None: ...

class GetRouteRequest(_message.Message):
    __slots__ = ("request_id", "routing_hint")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ROUTING_HINT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    routing_hint: str
    def __init__(self, request_id: _Optional[str] = ..., routing_hint: _Optional[str] = ...) -> None: ...

class GetRouteResponse(_message.Message):
    __slots__ = ("task_executor_url", "sidecar_ranks")
    TASK_EXECUTOR_URL_FIELD_NUMBER: _ClassVar[int]
    SIDECAR_RANKS_FIELD_NUMBER: _ClassVar[int]
    task_executor_url: str
    sidecar_ranks: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, task_executor_url: _Optional[str] = ..., sidecar_ranks: _Optional[_Iterable[int]] = ...) -> None: ...

class TaskExecutorStatus(_message.Message):
    __slots__ = ("status", "sidecar_ranks")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SIDECAR_RANKS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    sidecar_ranks: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., sidecar_ranks: _Optional[_Iterable[int]] = ...) -> None: ...

class HealthcheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthcheckResponse(_message.Message):
    __slots__ = ("status", "task_executor_statuses")
    class TaskExecutorStatusesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TaskExecutorStatus
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TaskExecutorStatus, _Mapping]] = ...) -> None: ...
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TASK_EXECUTOR_STATUSES_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    task_executor_statuses: _containers.MessageMap[str, TaskExecutorStatus]
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., task_executor_statuses: _Optional[_Mapping[str, TaskExecutorStatus]] = ...) -> None: ...
