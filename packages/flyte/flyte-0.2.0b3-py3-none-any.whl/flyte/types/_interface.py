from typing import Any, Dict, Type, cast

from flyteidl.core import interface_pb2

from flyte.models import NativeInterface


def guess_interface(interface: interface_pb2.TypedInterface) -> NativeInterface:
    """
    Returns the interface of the task with guessed types, as types may not be present in current env.
    """
    import flyte.types

    if interface is None:
        return NativeInterface({}, {})

    guessed_inputs: Dict[str, Type[Any]] = {}
    if interface.inputs is not None and len(interface.inputs.variables) > 0:
        guessed_inputs = flyte.types.TypeEngine.guess_python_types(cast(dict, interface.inputs.variables))

    guessed_outputs: Dict[str, Type[Any]] = {}
    if interface.outputs is not None and len(interface.outputs.variables) > 0:
        guessed_outputs = flyte.types.TypeEngine.guess_python_types(cast(dict, interface.outputs.variables))

    return NativeInterface.from_types(guessed_inputs, guessed_outputs)
