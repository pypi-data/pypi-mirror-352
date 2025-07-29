from typing import Any, Callable, Tuple, TypeVar

import flyte.errors
from flyte._context import internal_ctx
from flyte._internal.controllers import TraceInfo
from flyte._internal.runtime import convert
from flyte._internal.runtime.entrypoints import direct_dispatch
from flyte._logging import log, logger
from flyte._protos.workflow import task_definition_pb2
from flyte._task import TaskTemplate
from flyte.models import ActionID, NativeInterface, RawDataPath

R = TypeVar("R")


class LocalController:
    def __init__(self):
        logger.debug("LocalController init")

    @log
    async def submit(self, _task: TaskTemplate, *args, **kwargs) -> Any:
        """
        Submit a node to the controller
        """
        ctx = internal_ctx()
        tctx = ctx.data.task_context
        if not tctx:
            raise flyte.errors.RuntimeSystemError("BadContext", "Task context not initialized")

        inputs = await convert.convert_from_native_to_inputs(_task.native_interface, *args, **kwargs)
        serialized_inputs = inputs.proto_inputs.SerializeToString(deterministic=True)

        sub_action_id, sub_action_output_path = convert.generate_sub_action_id_and_output_path(
            tctx, _task.name, serialized_inputs, 0
        )
        sub_action_raw_data_path = RawDataPath(path=sub_action_output_path)

        out, err = await direct_dispatch(
            _task,
            controller=self,
            action=sub_action_id,
            raw_data_path=sub_action_raw_data_path,
            inputs=inputs,
            version=tctx.version,
            checkpoints=tctx.checkpoints,
            code_bundle=tctx.code_bundle,
            output_path=sub_action_output_path,
            run_base_dir=tctx.run_base_dir,
        )
        if err:
            exc = convert.convert_error_to_native(err)
            if exc:
                raise exc
            else:
                raise flyte.errors.RuntimeSystemError("BadError", "Unknown error")
        if _task.native_interface.outputs and out is not None:
            result = await convert.convert_outputs_to_native(_task.native_interface, out)
            return result
        return out

    async def finalize_parent_action(self, action: ActionID):
        pass

    async def stop(self):
        pass

    async def watch_for_errors(self):
        pass

    async def get_action_outputs(
        self, _interface: NativeInterface, _func: Callable, *args, **kwargs
    ) -> Tuple[TraceInfo, bool]:
        """
        This method returns the outputs of the action, if it is available.
        If not available it raises a  flyte.errors.ActionNotFoundError.
        :return:
        """
        ctx = internal_ctx()
        tctx = ctx.data.task_context
        if not tctx:
            raise flyte.errors.NotInTaskContextError("BadContext", "Task context not initialized")
        converted_inputs = convert.Inputs.empty()
        if _interface.inputs:
            converted_inputs = await convert.convert_from_native_to_inputs(_interface, *args, **kwargs)
            assert converted_inputs

        serialized_inputs = converted_inputs.proto_inputs.SerializeToString(deterministic=True)
        action_id, action_output_path = convert.generate_sub_action_id_and_output_path(
            tctx,
            _func.__name__,
            serialized_inputs,
            0,
        )
        assert action_output_path
        return (
            TraceInfo(
                action=action_id,
                interface=_interface,
                inputs_path=action_output_path,
            ),
            True,
        )

    async def record_trace(self, info: TraceInfo):
        """
        This method records the trace of the action.
        :param info: Trace information
        :return:
        """
        ctx = internal_ctx()
        tctx = ctx.data.task_context
        if not tctx:
            raise flyte.errors.NotInTaskContextError("BadContext", "Task context not initialized")

        if info.interface.outputs and info.output:
            # If the result is not an AsyncGenerator, convert it directly
            converted_outputs = await convert.convert_from_native_to_outputs(info.output, info.interface)
            assert converted_outputs
        elif info.error:
            # If there is an error, convert it to a native error
            converted_error = convert.convert_from_native_to_error(info.error)
            assert converted_error
        assert info.action
        assert info.duration

    async def submit_task_ref(self, _task: task_definition_pb2.TaskDetails, *args, **kwargs) -> Any:
        raise flyte.errors.ReferenceTaskError("Reference tasks cannot be executed locally, only remotely.")
