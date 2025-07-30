"""
Performs resolution of arguments for injection.
"""

import inspect
from typing import Any

import mcpf_core.core.routines as routines
from mcpf_core.core import constants, singletons
from mcpf_core.core.types import PipelineFunction

_VALID_PARAMETERS = {
    "data",
    "meta",
    "arg",
    "has_iterated_value",
    "iterated_value",
    "iterated_index",
}


def assert_parameters(func: PipelineFunction) -> None:
    """
    Asserts that all specified parameters are valid for argument injection.
    """
    sig = inspect.signature(func)
    invalid_parameters = [p for p in sig.parameters if p not in _VALID_PARAMETERS]
    if invalid_parameters:
        raise KeyError(
            f"Invalid parameters in function '{func.__name__}': {invalid_parameters}. Valid parameters are: {_VALID_PARAMETERS}"
        )


def inject_arguments(func: PipelineFunction, data: dict[str, Any], **kwargs):
    prepared_args = [data]
    prepared_kwargs = dict(**kwargs)

    sig = inspect.signature(func)

    needs_meta = "meta" in sig.parameters or "arg" in sig.parameters

    if needs_meta:
        meta = routines._get_meta_data_for_function(data, func)

    meta_specified = False
    if "meta" in sig.parameters:
        prepared_kwargs["meta"] = meta
        meta_specified = True

    if "has_iterated_value" in sig.parameters:
        prepared_kwargs["has_iterated_value"] = routines.is_iterated_value_available()

    if "iterated_value" in sig.parameters or "iterated_index" in sig.parameters:
        iteratedValue = singletons.LoopIterators().pop_iterated_value()
        if "iterated_value" in sig.parameters:
            prepared_kwargs["iterated_value"] = iteratedValue.value if iteratedValue else None
        if "iterated_index" in sig.parameters:
            prepared_kwargs["iterated_index"] = iteratedValue.index if iteratedValue else -1

    if "arg" in sig.parameters:
        arg = kwargs.get("arg", None)
        if constants.ARG_KEYWORD_ARGUMENTS in meta and isinstance(meta[constants.ARG_KEYWORD_ARGUMENTS], dict):
            arg = arg or {}
            arg = arg | meta[constants.ARG_KEYWORD_ARGUMENTS]
        prepared_kwargs["arg"] = arg

    result = func(*prepared_args, **prepared_kwargs)

    if result is not None and isinstance(result, dict):
        data = result

    if meta_specified:
        routines.set_meta_in_data(data, meta)

    return data
