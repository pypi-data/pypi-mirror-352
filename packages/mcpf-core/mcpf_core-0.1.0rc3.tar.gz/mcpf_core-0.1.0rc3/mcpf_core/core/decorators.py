"""
This module contains decorators for pipeline functions.
"""
import functools
import inspect


def with_default_arguments(default_arguments: dict[str, str]):
    """
    This decorator allows you to set default arguments for a pipeline function
    and will merge them with the arguments provided in the function call.
    Arguments provided by parameter 'arg' will override the default ones."

    ```python
    @with_default_arguments({
        "input": constants.DEFAULT_IO_DATA_LABEL,
        "output": constants.DEFAULT_IO_DATA_LABEL,
    })
    def my_pipeline_function(data: dict[str, str], arg: dict[str, str]):
        # Your function implementation here
        ...
    ```

    is the equivalent of:
    ```python
    def my_pipeline_function(data: dict[str, Any], meta: dict[str, Any]):
        # default_arguments_values
        arg = {
            "input": constants.DEFAULT_IO_DATA_LABEL,
            "output": constants.DEFAULT_IO_DATA_LABEL,
        }
        # merging default values with current argument values
        if meta[constants.ARGUMENTS]:
            arg = arg | meta[constants.ARGUMENTS]

        # Your function implementation here
        ...
    ```

    """
    if not isinstance(default_arguments, dict):
        raise TypeError("default_arguments must be a dictionary")

    def my_decorator(func):
        sig = inspect.signature(func)
        apply = "arg" in sig.parameters

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if apply:
                arg = default_arguments.copy()
                passed_arg = kwargs.get("arg", None)
                if passed_arg is not None:
                    arg |= passed_arg

                kwargs["arg"] = arg
            return func(*args, **kwargs)

        return wrapped

    return my_decorator
