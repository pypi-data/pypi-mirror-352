import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HealthStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEALTH_ALL_GOOD: _ClassVar[HealthStatus]
    HEALTH_MEMORY_PRESSURE: _ClassVar[HealthStatus]
    HEALTH_OFFLINE: _ClassVar[HealthStatus]
HEALTH_ALL_GOOD: HealthStatus
HEALTH_MEMORY_PRESSURE: HealthStatus
HEALTH_OFFLINE: HealthStatus

class RegisterRequest(_message.Message):
    __slots__ = ("rank", "group", "dtype", "send_slot_numel", "recv_slot_numel", "concurrent_copy")
    RANK_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    SEND_SLOT_NUMEL_FIELD_NUMBER: _ClassVar[int]
    RECV_SLOT_NUMEL_FIELD_NUMBER: _ClassVar[int]
    CONCURRENT_COPY_FIELD_NUMBER: _ClassVar[int]
    rank: int
    group: _containers.RepeatedScalarFieldContainer[int]
    dtype: str
    send_slot_numel: int
    recv_slot_numel: int
    concurrent_copy: bool
    def __init__(self, rank: _Optional[int] = ..., group: _Optional[_Iterable[int]] = ..., dtype: _Optional[str] = ..., send_slot_numel: _Optional[int] = ..., recv_slot_numel: _Optional[int] = ..., concurrent_copy: bool = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("status", "shm_size", "local_rank", "num_local_sidecars")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SHM_SIZE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_RANK_FIELD_NUMBER: _ClassVar[int]
    NUM_LOCAL_SIDECARS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    shm_size: int
    local_rank: int
    num_local_sidecars: int
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., shm_size: _Optional[int] = ..., local_rank: _Optional[int] = ..., num_local_sidecars: _Optional[int] = ...) -> None: ...

class RankGroup(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, ranks: _Optional[_Iterable[int]] = ...) -> None: ...

class SendRequest(_message.Message):
    __slots__ = ("id", "dst_ranks", "shard_rank", "data", "chunk_id", "num_chunks")
    ID_FIELD_NUMBER: _ClassVar[int]
    DST_RANKS_FIELD_NUMBER: _ClassVar[int]
    SHARD_RANK_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    dst_ranks: _containers.RepeatedCompositeFieldContainer[RankGroup]
    shard_rank: int
    data: bytes
    chunk_id: int
    num_chunks: int
    def __init__(self, id: _Optional[str] = ..., dst_ranks: _Optional[_Iterable[_Union[RankGroup, _Mapping]]] = ..., shard_rank: _Optional[int] = ..., data: _Optional[bytes] = ..., chunk_id: _Optional[int] = ..., num_chunks: _Optional[int] = ...) -> None: ...

class SendResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class ReceiveRequest(_message.Message):
    __slots__ = ("id", "chunk_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    chunk_id: int
    def __init__(self, id: _Optional[str] = ..., chunk_id: _Optional[int] = ...) -> None: ...

class ReceiveResponse(_message.Message):
    __slots__ = ("status", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    data: bytes
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ..., data: _Optional[bytes] = ...) -> None: ...

class MarkDoneRequest(_message.Message):
    __slots__ = ("id", "chunk_id", "shard_rank")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    SHARD_RANK_FIELD_NUMBER: _ClassVar[int]
    id: str
    chunk_id: int
    shard_rank: int
    def __init__(self, id: _Optional[str] = ..., chunk_id: _Optional[int] = ..., shard_rank: _Optional[int] = ...) -> None: ...

class MarkDoneResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class UnlinkRequest(_message.Message):
    __slots__ = ("id", "chunk_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    chunk_id: int
    def __init__(self, id: _Optional[str] = ..., chunk_id: _Optional[int] = ...) -> None: ...

class UnlinkResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class PrepareReceiveRequest(_message.Message):
    __slots__ = ("id", "data", "src_rank", "chunk_id", "num_chunks")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SRC_RANK_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    id: str
    data: bytes
    src_rank: int
    chunk_id: int
    num_chunks: int
    def __init__(self, id: _Optional[str] = ..., data: _Optional[bytes] = ..., src_rank: _Optional[int] = ..., chunk_id: _Optional[int] = ..., num_chunks: _Optional[int] = ...) -> None: ...

class PrepareReceiveResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...

class CheckHealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CheckHealthResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: HealthStatus
    def __init__(self, status: _Optional[_Union[HealthStatus, str]] = ...) -> None: ...

class ReportMemoryRequest(_message.Message):
    __slots__ = ("pressure",)
    PRESSURE_FIELD_NUMBER: _ClassVar[int]
    pressure: int
    def __init__(self, pressure: _Optional[int] = ...) -> None: ...

class ReportMemoryResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.Status
    def __init__(self, status: _Optional[_Union[_common_pb2.Status, str]] = ...) -> None: ...
