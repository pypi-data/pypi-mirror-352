import inspect
import json
import sys
from typing import Any, Optional, Tuple, Union

import mcpf_core.core.constants as constants
import mcpf_core.core.singletons as singleton
from mcpf_core.core.types import PipelineFunction


def get_meta_data(data: dict[str, Any], func: Optional[PipelineFunction] = None) -> dict[str, Any]:
    """
    It extracts the json string "meta" from "data" and adds the current yaml arguments of the caller to "meta".
    Returns:
        A dictionary, which contains the content of the "meta" as well as the current arguments of the caller function.
    """
    caller_func = inspect.getframeinfo(sys._getframe(1))[2]
    return _get_meta_data_for_function(data, caller_func)


def _get_meta_data_for_function(data: dict[str, Any], func: Union[PipelineFunction, str]) -> dict[str, Any]:
    """
    Extracts and updates metadata for a given function.

    This function retrieves the JSON string "meta" from the provided `data` dictionary,
    parses it into a dictionary, and adds the current YAML arguments of the caller
    function to the metadata. The caller function is identified either by its name
    (if `func` is a string) or by the `__name__` attribute (if `func` is a `PipelineFunction`).

    Note: This function is intended for internal use and should not be called directly.
    Use `get_meta_data` function instead from within pipeline functions.

    Args:
        data (dict[str, Any]): A dictionary the metadata is derived from.
        func (Union[PipelineFunction, str]): The function or its name for which
            arguments are to be injected into the metadata.

    Returns:
        dict[str, Any]: A dictionary containing the parsed metadata along with the
        current arguments of the caller function.

    Raises:
        ValueError: If no metadata could be derived from the `data` dictionary.
    """
    if constants.ARG_KEYWORD_META not in data:
        raise ValueError("Error! No metadata in the arguments")
    json_meta = data[constants.ARG_KEYWORD_META]
    meta = json.loads(json_meta)
    caller_func = func if type(func) == str else func.__name__
    param_singleton = singleton.Arguments()
    meta[constants.ARG_KEYWORD_ARGUMENTS] = param_singleton.get_upcoming_arguments(caller_func)
    return meta


def set_meta_in_data(data: dict[str, Any], meta: dict[str, Any]):
    """
    It packs back the meta information given in terms of a dictionary into json string and stores it in "data".
    Args:
        data:
        meta:

    Returns:
        data
    """
    del meta[constants.ARG_KEYWORD_ARGUMENTS]
    json_meta = json.dumps(meta)
    data[constants.ARG_KEYWORD_META] = json_meta


def register_loop_iterator_list(iterator_list: list, deep_copy: bool = False):
    """
    It registers a list of loop iterator values.
    Args:
        iterator_list:
        deep_copy:
    """
    loop_singleton = singleton.LoopIterators()
    loop_singleton.register_new_iterator_list(iterator_list, deep_copy)


def is_iterated_value_available() -> bool:
    """
    Returns true if the iterated value is still available and can be consumed with `pop_loop_iterator`.
    """
    loop_singleton = singleton.LoopIterators()
    return loop_singleton.is_iterated_value_available()


def pop_loop_iterator() -> Any:
    """
    It returns with the current iterator value, if it wasn't returned yet.

    Note: Use `pop_iterated_value` instead. It performs the same function,
    but its name better conveys the function's meaning.

    Returns:
        object: the current iterator value or None.
    """
    return pop_iterated_value()


def pop_iterated_value() -> Any:
    """
    It returns the current iterated value.

    If there was none, or the iterated value was already consumed by previously calling
    `pop_iterated_value` (either by the calling function or a preceding function in the same
    pipeline), it returns None.

    Check with `is_iterated_value_available` if the value was already consumed,
    or if the value is available but actually `None`.

    Returns:
        the current iterated value or None, depending on the state of `is_iterated_value_available`.
    """
    value, _ = pop_iterated_value_and_index()
    return value


def pop_iterated_value_and_index() -> Tuple[Any, int]:
    """
    It returns the current iterated value and the current loop index.

    If there was none, or the iterated value was already consumed by previously calling
    `pop_iterated_value` (either by the calling function or a preceding function in the same
    pipeline), it returns None.

    Check with `is_iterated_value_available` if the value was already consumed,
    or if the value is available but actually `None`.

    Returns:
        a tuple of the current iterated value and index, or `(None, -1)`,
        depending on the state of `is_iterated_value_available`.
    """
    loop_singleton = singleton.LoopIterators()
    iterated_value = loop_singleton.pop_iterated_value()
    return (iterated_value.value, iterated_value.index) if iterated_value else (None, -1)


def get_current_input_dir(meta: dict[str, Any]) -> str:
    """
    It returns with current input directory.
    Args:
        meta: the required information will be extracted from "meta".
    """
    index_of_dirs = meta[constants.TMP_PATH_INDEX]
    input_dir = meta[constants.TMP_PATHS][index_of_dirs]
    return input_dir


def get_current_tmp_dir(meta: dict[str, Any]) -> str:
    """
    It returns with current tmp/output directory
    Args:
        meta: the required information will be extracted from "meta".
    """
    index_of_dirs = next_tmp_dir_index(meta)
    output_dir = meta[constants.TMP_PATHS][index_of_dirs]
    return output_dir


def get_final_output_dir(meta: dict[str, Any]) -> str:
    """
    It returns with directory to which the final output should be stored.
    Args:
        meta: the required information will be extracted from "meta".
    """
    index_of_dirs = next_tmp_dir_index(meta)
    output_dir = meta[constants.TMP_PATHS][-1]
    return output_dir


def next_tmp_dir_index(meta: dict[str, Any]) -> int:
    """
    It returns with the index of current tmp/output directory.
    Args:
        meta: the required information will be extracted from "meta".
    """
    index_of_dirs = meta[constants.TMP_PATH_INDEX]
    if len(meta[constants.TMP_PATHS]) - 1 > index_of_dirs:
        index_of_dirs += 1
    return index_of_dirs


def set_current_output_dir_to_input_dir(meta: dict[str, Any]):
    """
    It sets the current tmp directory to the current input directory and the upcoming tmp directory to the current one.
    """
    meta[constants.TMP_PATH_INDEX] = next_tmp_dir_index(meta)


def get_db_config(meta: dict[str, Any], db_type: str) -> dict[str, Any] | None:
    """
    It returns with "database_configs" part of the current yaml configuration.
    Args:
        meta:
        db_type:

    Returns:
        A dictionary, which contains how to access to the database, whose type corresponds to the given db type.
    """
    if constants.DB_CONFIG not in meta or len(meta[constants.DB_CONFIG]) == 0:
        return None
    ret_val_dict: dict[str, Any] = meta[constants.DB_CONFIG][0]
    index = 1
    while ret_val_dict["type"] != db_type and index < len(meta[constants.DB_CONFIG]):
        ret_val_dict = meta[constants.DB_CONFIG][index]
        index += 1
    if ret_val_dict["type"] == db_type:
        return ret_val_dict
    else:
        return None
