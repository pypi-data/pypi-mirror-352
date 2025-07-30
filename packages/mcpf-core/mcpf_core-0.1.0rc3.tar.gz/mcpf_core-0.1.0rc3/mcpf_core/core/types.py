from dataclasses import dataclass, field
from typing import Any, Optional, Protocol, Union

JSONType = Union[dict[str, "JSONType"], list["JSONType"], str, int, float, bool, None]


@dataclass
class PipelineIteratedValue:
    """Class to hold the iterated value of a pipeline"""

    value: Any
    index: int


class PipelineFunction(Protocol):
    """Generic Function signature for every MCPF function

    This type defines the expected signature of every pipeline function.

    """

    def __call__(
        data: dict[str, Any],
        meta: Optional[dict[str, Any]] = None,
        has_iterated_value: bool = False,
        iterated_value: Optional[Any] = None,
        iterated_index: int = -1,
        arg: Optional[dict[str, JSONType]] = None,
    ) -> dict[str, Any]:
        """Generic Function signature for every MCPF function

        Generic Function signature for every MCPF function.

        Only the data parameter is mandatory. The rest of the parameters need not
        be declared in the function signature if you don't need them. Each optional
        parameter will be injected by the pipeline engine, so you can selectively
        query the information you actually need.

        Args:
            data (dict[str, Any]): The main data dictionary to process.
                It is up to the caller to define any conventions to pass data down
                the pipeline. This parameter is mandatory.
            meta (Optional[dict[str, Any]]): Contains metadata derived from the pipeline
                configuration. You can change metadata in the function, and the changed
                metadata will be passed to the next function in the pipeline.
            has_iterated_value (bool): If this function is to be used within a loop or
                other iterable construct, you can query whether a value for the current
                iteration step is still available.
            iterated_value (Optional[Any]): The current iterated value, if any.
            iterated_index (int): The index of the current iterated value or -1 if not
                within an iteration step.
            arg (Optional[dict[str, JSONType]]): Contains a mapping of names to
                argument names to be used as keys in the data dictionary. The arg
                dictionary is extracted from the meta dictionary.

        Returns:
            dict[str, Any]: The potentially modified data dictionary ready to be passed
                to the next function in the pipeline. If None, the `data` argument
                will be implicitly returned. Even if you return None, all changes
                applied to the data dictionary will still be propagated to the next
                function in the pipeline.

                If you want to prevent changes to the data dictionary from being
                propagated, you can make a deep copy of the data dictionary and
                only change the copy within the function.
        """
        ...


@dataclass
class DatabaseConfig:
    type: str
    url: str
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    org: Optional[str] = None
    bucket: Optional[str] = None


@dataclass
class PipelineConfig:
    input_path: str
    output_path: str
    entry_point: str
    imports: list[str]
    pipelines: list[dict[str, list[dict[str, str]]]]
    input_file_name: str = field(default=None)
    tmp_paths: list[str] = field(default=None)
    pipeline_extension: list[dict[str, list[dict[str, str]]]] = field(default=None)
    further_configuration: Optional[list[dict[str, str]]] = field(default=None)
    database_configs: Optional[list[DatabaseConfig]] = field(default=None)
