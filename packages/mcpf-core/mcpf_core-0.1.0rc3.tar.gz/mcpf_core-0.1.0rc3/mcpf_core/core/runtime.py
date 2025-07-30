#! /usr/bin/env python3
# TODO
# config levels
# more and embedded loops (list of loop list and iterator list)

import dataclasses
import functools
import importlib
import json
import os.path
from pathlib import Path
from types import ModuleType
from typing import Any, Optional

import risc_lasagna as lasagna
import risc_lasagna.layer as layer
from toolz import pipe

import mcpf_core.core.constants as constants
import mcpf_core.core.routines as routines
import mcpf_core.core.singletons as singletons
from mcpf_core.core import arginjector
from mcpf_core.core.types import JSONType, PipelineConfig, PipelineFunction

dept_of_nested_loops = 0
real_dept_of_loop_kernel_hierarchy = 0
current_max_dept_of_nested_loops = 0
loop_kernel_pipelines: list[
    tuple[str, list[PipelineFunction]]
] = []  # it contains the child pipeline of loops in the order of execution

dict_of_called_pipeline_element: dict[str, int] = {}


def load_pipeline_config(args: Optional[list[str]]) -> PipelineConfig:
    """
    Loads the pipeline configuration using the "lasagna" package to parse YAML configuration files and compose a single code pipeline configuration.

    Args:
        args (Optional[list[str]]): list of command-line arguments. If None or empty, default configuration is used. Otherwise, the list contains paths to YAML configuration files.

    Returns:
        PipelineConfig: A dataclass containing the merged pipeline configuration.

    Raises:
        FileNotFoundError: If any of the provided YAML configuration files do not exist.
        NotImplementedError: If the configuration is missing required fields such as 'imports', 'pipelines', or 'entry_point'.
    """
    # set the environment variable with a prefix
    if not args or len(args) == 0:
        return lasagna.build(
            PipelineConfig,
            [
                layer.DataClassDefaultLayer(
                    PipelineConfig(
                        ".", ".", "default_p", [], [{"default_p": [{"version": "~"}, {"help": "~"}]}], "", []
                    )
                ),
            ],
        )
    else:
        extensions = []
        imports = dict[str, str]()
        converted_list = map(Path, args)
        yaml_layers = list(map(layer.YamlLayer, converted_list))
        for l in yaml_layers[:-1]:
            if constants.ARG_KEYWORD_PIPELINE_EXT in l.map:
                extensions.append(l.map[constants.ARG_KEYWORD_PIPELINE_EXT])
        for l in yaml_layers:
            if constants.ARG_KEYWORD_IMPORTS in l.map:
                imports |= {imp: imp for imp in l.map[constants.ARG_KEYWORD_IMPORTS]}
        l_config = lasagna.build(
            PipelineConfig,
            [
                *yaml_layers,
                layer.DataClassDefaultLayer(
                    PipelineConfig(
                        ".", ".", "default_p", [], [{"default_p": [{"version": "~"}, {"help": "~"}]}], "", []
                    )
                ),
            ],
        )
        l_config.imports = list[str](imports.values())
        first_element = True
        for sub_pipeline in l_config.pipelines:
            if first_element:
                first_element = False
            else:
                for key in sub_pipeline:
                    l_config.pipelines[0][key] = sub_pipeline[key]

        del l_config.pipelines[1:]

        if len(extensions) > 0:
            for extension in reversed(extensions):
                if len(extension) > 0:
                    for extension_element in extension:
                        for pipeline_element in extension_element:
                            l_config.pipelines[0][pipeline_element] = extension_element[pipeline_element]
        return l_config


def increment_dept_of_nested_loops():
    """
    This function keeps track the dept of the nested loops.
    """
    global current_max_dept_of_nested_loops
    global dept_of_nested_loops
    global real_dept_of_loop_kernel_hierarchy
    dept_of_nested_loops += 1
    real_dept_of_loop_kernel_hierarchy += 1
    if real_dept_of_loop_kernel_hierarchy > current_max_dept_of_nested_loops:
        current_max_dept_of_nested_loops = real_dept_of_loop_kernel_hierarchy


def init_iterator(data: dict[str, Any]) -> dict[str, Any]:
    """
    Each execution of every loop kernel starts with this function. It initializes the current value of the
    loop iterator.
    """
    global dept_of_nested_loops
    loop_singleton = singletons.LoopIterators()
    loop_singleton.init_current_iterator(dept_of_nested_loops - 1)
    return data


def loop_interpreter(data: dict[str, Any]) -> dict[str, Any]:
    """
    This function is used to implement a loop in the code pipeline.
    """
    global dept_of_nested_loops  # Handling iterator list
    global current_max_dept_of_nested_loops
    global loop_kernel_pipelines
    global real_dept_of_loop_kernel_hierarchy  # Handling loop kernels
    loop_singleton = singletons.LoopIterators()
    param_singleton = singletons.Arguments()
    if len(loop_kernel_pipelines) > 0:
        increment_dept_of_nested_loops()
        kernel_entry = loop_kernel_pipelines[real_dept_of_loop_kernel_hierarchy - 1]
        if kernel_entry[0] not in dict_of_called_pipeline_element:
            dict_of_called_pipeline_element[kernel_entry[0]] = real_dept_of_loop_kernel_hierarchy
        else:
            real_dept_of_loop_kernel_hierarchy = dict_of_called_pipeline_element[kernel_entry[0]]
            param_singleton.overwrite_current_depth(real_dept_of_loop_kernel_hierarchy - 1)
        kernel = loop_kernel_pipelines[real_dept_of_loop_kernel_hierarchy - 1][1]
        param_singleton.replace_current_argument_lists()
        try:
            while loop_singleton.size_of_an_iterator_list(dept_of_nested_loops - 1) > 0:
                data = pipe(data, *kernel)
                param_singleton.renew_loop_argument_lists()
        finally:
            param_singleton.restore_last_buffered_argument_list()
            routines.pop_loop_iterator()  # it is needed just in that case if no one used up the iterator
            loop_singleton.remove_an_iterator_list(dept_of_nested_loops - 1)
            if dept_of_nested_loops == real_dept_of_loop_kernel_hierarchy:
                real_dept_of_loop_kernel_hierarchy -= 1
            dept_of_nested_loops -= 1
            if dept_of_nested_loops == 0:
                del loop_kernel_pipelines[:current_max_dept_of_nested_loops]
                current_max_dept_of_nested_loops = 0
                dict_of_called_pipeline_element.clear()
    return data


def _wrap_pipeline_function_injector(func):
    """
    This function is used to inject the optional arguments into the function itself.
    That way you need less boilerplate code in the function itself.
    """

    arginjector.assert_parameters(func)

    @functools.wraps(func)
    def wrapper(data: dict[str, Any], *args, **kwargs):
        return arginjector.inject_arguments(func, data, *args, **kwargs)

    return wrapper


def validate_pipeline(
    config: PipelineConfig,
    current_pipeline: str,
    modules: dict[str, ModuleType],
    current_param_lists: list[dict[str, JSONType]],
    param_lists_of_loops: list[list[Any]],
    evaluated_sub_pipelines=None,  # avoiding to validate recursive calls
    is_recursive: bool = False,
) -> list[PipelineFunction]:
    """
    This function compose the code pipeline and pipeline of the loop kernels according the given yaml configuration,
    stores the function arguments given in the yaml configuration in a structured way and
    validate each pipeline (e.g.: it checks the existence of the given functions in the enumerated python modules).
    """
    global loop_kernel_pipelines
    # preparing available building blocks
    # this_module = sys.modules[__name__]
    if evaluated_sub_pipelines is None:
        evaluated_sub_pipelines = []
    available_functions: dict[str, list[PipelineFunction]] = {}
    for module in modules:
        function_list = dir(modules[module])
        available_functions[module] = function_list

    pipeline: list[PipelineFunction] = []
    for func_const in config.pipelines[0][current_pipeline]:
        for func in func_const:
            if func[: len(constants.ARG_KEYWORD_LOOP)] == constants.ARG_KEYWORD_LOOP:
                if not is_recursive:
                    if func_const[func] in evaluated_sub_pipelines:
                        is_recursive = True
                    child_pipeline = [init_iterator]
                    kernel_arguments_lists = []
                    param_lists_of_loops.append(kernel_arguments_lists)
                    loop_kernel_pipelines.append((func_const[func], child_pipeline))
                    pipeline.append(loop_interpreter)
                    child_pipeline.extend(
                        validate_pipeline(
                            config,
                            func_const[func],
                            modules,
                            kernel_arguments_lists,
                            param_lists_of_loops,
                            evaluated_sub_pipelines + [func_const[func]],
                            is_recursive,
                        )
                    )
                    # f = getattr(this_module, 'init_iterator')
            elif func in config.pipelines[0]:
                if func not in evaluated_sub_pipelines:
                    evaluated_sub_pipelines.append(func)
                    sub_pipeline = validate_pipeline(
                        config,
                        func,
                        modules,
                        current_param_lists,
                        param_lists_of_loops,
                        evaluated_sub_pipelines + [func],
                        is_recursive,
                    )
                    pipeline.extend(sub_pipeline.copy())
            else:
                not_found = True
                for module in available_functions:
                    if func in available_functions[module]:
                        f: PipelineFunction = getattr(modules[module], func)
                        pipeline.append(_wrap_pipeline_function_injector(f))
                        current_param_lists.append(func_const)
                        not_found = False
                        break
                if not_found:
                    raise NotImplementedError("Error: None of the imported modules contain the function " + func + "!")
    return pipeline


def run_pipeline(
    config: PipelineConfig, pipeline: list[PipelineFunction], current_param_lists: list[dict[str, str]]
) -> dict[str, Any]:
    """
    It initializes the "meta" and execute the code pipeline composed from the given configuration.
    """
    config.tmp_paths.insert(0, config.input_path)
    config.tmp_paths.append(config.output_path)
    tmp_absolut_paths = []
    for path in config.tmp_paths:
        tmp_absolut_paths.append(os.path.abspath(path))
    meta = {constants.TMP_PATH_INDEX: 0}
    meta[constants.TMP_PATHS] = tmp_absolut_paths
    if config.further_configuration:
        for key_value_pair in config.further_configuration:
            for key in key_value_pair:
                meta[key] = key_value_pair[key]
    if config.database_configs:
        db_configs = []
        for config_element in config.database_configs:
            config_dict = {}
            for f in dataclasses.fields(config_element):
                config_dict[f.name] = getattr(config_element, f.name)
            db_configs.append(config_dict)
        meta[constants.DB_CONFIG] = db_configs
    json_meta = json.dumps(meta)
    data = {constants.ARG_KEYWORD_META: json_meta}
    retval: dict[str, Any] = pipe(data, *pipeline)
    return retval


def run(*args: str) -> dict[str, Any]:
    """
    Run pipeline programmatically as if called from command line
    """
    singletons.LoopIterators.reset()
    singletons.Arguments.reset()
    for arg in args:
        if not os.path.isfile(arg):
            raise FileNotFoundError("Error: config file " + arg + " does not exist.")
    c = load_pipeline_config(args)
    if not c.imports or not c.pipelines or not c.entry_point:
        raise NotImplementedError("Error: Missing 'imports', 'pipelines' or 'entry_point' in the config file.")
    else:
        imported_modules: dict[str, ModuleType] = {}
        for module_name in c.imports:
            i = importlib.import_module(module_name)
            imported_modules[module_name] = i

        param_lists: list[dict[str, str]] = []
        arguments_of_sub_pipelines: list[list[Any]] = []
        pipeline_string = validate_pipeline(c, c.entry_point, imported_modules, param_lists, arguments_of_sub_pipelines)
        p = singletons.Arguments()
        p.current_param_lists = param_lists
        p.param_lists_of_loops = arguments_of_sub_pipelines
        return run_pipeline(c, pipeline_string, param_lists)
