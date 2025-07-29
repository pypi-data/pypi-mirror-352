from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from flyteidl.core import execution_pb2, literals_pb2

import flyte.errors
import flyte.storage as storage
from flyte._protos.workflow import run_definition_pb2, task_definition_pb2
from flyte.models import ActionID, NativeInterface, TaskContext
from flyte.types import TypeEngine


@dataclass(frozen=True)
class Inputs:
    proto_inputs: run_definition_pb2.Inputs

    @classmethod
    def empty(cls) -> "Inputs":
        return cls(proto_inputs=run_definition_pb2.Inputs())


@dataclass(frozen=True)
class Outputs:
    proto_outputs: run_definition_pb2.Outputs


@dataclass
class Error:
    err: execution_pb2.ExecutionError


# ------------------------------- CONVERT Methods ------------------------------- #


def _clean_error_code(code: str) -> Tuple[str, str | None]:
    """
    The error code may have a server injected code and is of the form `RetriesExhausedError|<code>` or `<code>`.

    :param code:
    :return: "user code", optional server code
    """
    if "|" in code:
        server_code, user_code = code.split("|", 1)
        return user_code.strip(), server_code.strip()
    return code.strip(), None


async def convert_inputs_to_native(inputs: Inputs, python_interface: NativeInterface) -> Dict[str, Any]:
    literals = {named_literal.name: named_literal.value for named_literal in inputs.proto_inputs.literals}
    native_vals = await TypeEngine.literal_map_to_kwargs(
        literals_pb2.LiteralMap(literals=literals), python_interface.get_input_types()
    )
    return native_vals


async def convert_from_native_to_inputs(interface: NativeInterface, *args, **kwargs) -> Inputs:
    kwargs = interface.convert_to_kwargs(*args, **kwargs)
    if len(kwargs) == 0:
        return Inputs.empty()
    # fill in defaults if missing
    for input_name, (input_type, default_value) in interface.inputs.items():
        if input_name not in kwargs:
            if default_value is not None:
                kwargs[input_name] = default_value
            # todo: fill in Nones for optional inputs
    if len(kwargs) < len(interface.inputs):
        raise ValueError(
            f"Received {len(kwargs)} inputs but interface has {len(interface.inputs)}. "
            f"Please provide all required inputs."
        )
    literal_map = await TypeEngine.dict_to_literal_map(kwargs, interface.get_input_types())
    return Inputs(
        proto_inputs=run_definition_pb2.Inputs(
            literals=[run_definition_pb2.NamedLiteral(name=k, value=v) for k, v in literal_map.literals.items()]
        )
    )


async def convert_from_native_to_outputs(o: Any, interface: NativeInterface) -> Outputs:
    # Always make it a tuple even if it's just one item to simplify logic below
    if not isinstance(o, tuple):
        o = (o,)

    assert len(interface.outputs) == len(interface.outputs), (
        f"Received {len(o)} outputs but interface has {len(interface.outputs)}"
    )
    named = []
    for (output_name, python_type), v in zip(interface.outputs.items(), o):
        lit = await TypeEngine.to_literal(v, python_type, TypeEngine.to_literal_type(python_type))
        named.append(run_definition_pb2.NamedLiteral(name=output_name, value=lit))

    return Outputs(proto_outputs=run_definition_pb2.Outputs(literals=named))


async def convert_outputs_to_native(interface: NativeInterface, outputs: Outputs) -> Union[Any, Tuple[Any, ...]]:
    lm = literals_pb2.LiteralMap(
        literals={named_literal.name: named_literal.value for named_literal in outputs.proto_outputs.literals}
    )
    kwargs = await TypeEngine.literal_map_to_kwargs(lm, interface.outputs)
    if len(kwargs) == 0:
        return None
    elif len(kwargs) == 1:
        return next(iter(kwargs.values()))
    else:
        # Return as tuple if multiple outputs, make sure to order correctly as it seems proto maps can change ordering
        return tuple(kwargs[k] for k in interface.outputs.keys())


def convert_error_to_native(err: execution_pb2.ExecutionError | Exception | Error) -> Exception | None:
    if not err:
        return None

    if isinstance(err, Exception):
        return err

    if isinstance(err, Error):
        err = err.err

    user_code, server_code = _clean_error_code(err.code)
    match err.kind:
        case execution_pb2.ExecutionError.UNKNOWN:
            return flyte.errors.RuntimeUnknownError(code=user_code, message=err.message, worker=err.worker)
        case execution_pb2.ExecutionError.USER:
            if "OOM" in err.code.upper():
                return flyte.errors.OOMError(code=user_code, message=err.message, worker=err.worker)
            elif "Interrupted" in err.code:
                return flyte.errors.TaskInterruptedError(code=user_code, message=err.message, worker=err.worker)
            elif "PrimaryContainerNotFound" in err.code:
                return flyte.errors.PrimaryContainerNotFoundError(
                    code=user_code, message=err.message, worker=err.worker
                )
            elif "RetriesExhausted" in err.code:
                return flyte.errors.RetriesExhaustedError(code=user_code, message=err.message, worker=err.worker)
            elif "Unknown" in err.code:
                return flyte.errors.RuntimeUnknownError(code=user_code, message=err.message, worker=err.worker)
            elif "InvalidImageName" in err.code:
                return flyte.errors.InvalidImageNameError(code=user_code, message=err.message, worker=err.worker)
            elif "ImagePullBackOff" in err.code:
                return flyte.errors.ImagePullBackOffError(code=user_code, message=err.message, worker=err.worker)
            return flyte.errors.RuntimeUserError(code=user_code, message=err.message, worker=err.worker)
        case execution_pb2.ExecutionError.SYSTEM:
            return flyte.errors.RuntimeSystemError(code=user_code, message=err.message, worker=err.worker)
    return None


def convert_from_native_to_error(err: BaseException) -> Error:
    if isinstance(err, flyte.errors.RuntimeUnknownError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.UNKNOWN,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    elif isinstance(err, flyte.errors.RuntimeUserError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.USER,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    elif isinstance(err, flyte.errors.RuntimeSystemError):
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.SYSTEM,
                code=err.code,
                message=str(err),
                worker=err.worker,
            )
        )
    else:
        return Error(
            err=execution_pb2.ExecutionError(
                kind=execution_pb2.ExecutionError.UNKNOWN,
                code=type(err).__name__,
                message=str(err),
                worker="UNKNOWN",
            )
        )


def hash_data(data: Union[str, bytes]) -> str:
    """
    Generate a hash for the given data. If the data is a string, it will be encoded to bytes before hashing.
    :param data: The data to hash, can be a string or bytes.
    :return: A hexadecimal string representation of the hash.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    digest = hashlib.sha256(data).digest()
    return base64.b64encode(digest).decode("utf-8")


def generate_sub_action_id_and_output_path(
    tctx: TaskContext,
    task_spec_or_name: task_definition_pb2.TaskSpec | str,
    serialized_inputs: str | bytes,
    invoke_seq: int,
) -> Tuple[ActionID, str]:
    """
    Generate a sub-action ID and output path based on the current task context, task name, and inputs.

    action name = current action name + task name + input hash + group name (if available)
    :param tctx:
    :param task_spec_or_name: task specification or task name. Task name is only used in case of trace actions.
    :param serialized_inputs:
    :param invoke_seq: The sequence number of the invocation, used to differentiate between multiple invocations.
    :return:
    """
    current_action_id = tctx.action
    current_output_path = tctx.run_base_dir
    inputs_hash = hash_data(serialized_inputs)
    if isinstance(task_spec_or_name, task_definition_pb2.TaskSpec):
        task_hash = hash_data(task_spec_or_name.SerializeToString(deterministic=True))
    else:
        task_hash = task_spec_or_name
    sub_action_id = current_action_id.new_sub_action_from(
        task_hash=task_hash,
        input_hash=inputs_hash,
        group=tctx.group_data.name if tctx.group_data else None,
        task_call_seq=invoke_seq,
    )
    sub_run_output_path = storage.join(current_output_path, sub_action_id.name)
    return sub_action_id, sub_run_output_path
