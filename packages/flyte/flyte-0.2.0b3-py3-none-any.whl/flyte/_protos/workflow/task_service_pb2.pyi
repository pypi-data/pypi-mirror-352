from flyte._protos.validate.validate import validate_pb2 as _validate_pb2
from flyte._protos.workflow import task_definition_pb2 as _task_definition_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DeployTaskRequest(_message.Message):
    __slots__ = ["task_id", "spec"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    SPEC_FIELD_NUMBER: _ClassVar[int]
    task_id: _task_definition_pb2.TaskIdentifier
    spec: _task_definition_pb2.TaskSpec
    def __init__(self, task_id: _Optional[_Union[_task_definition_pb2.TaskIdentifier, _Mapping]] = ..., spec: _Optional[_Union[_task_definition_pb2.TaskSpec, _Mapping]] = ...) -> None: ...

class DeployTaskResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetTaskDetailsRequest(_message.Message):
    __slots__ = ["task_id"]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: _task_definition_pb2.TaskIdentifier
    def __init__(self, task_id: _Optional[_Union[_task_definition_pb2.TaskIdentifier, _Mapping]] = ...) -> None: ...

class GetTaskDetailsResponse(_message.Message):
    __slots__ = ["details"]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    details: _task_definition_pb2.TaskDetails
    def __init__(self, details: _Optional[_Union[_task_definition_pb2.TaskDetails, _Mapping]] = ...) -> None: ...
