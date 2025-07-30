import copy
from typing import Any, Iterable, Optional

from mcpf_core.core.types import JSONType, PipelineIteratedValue


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def reset(cls):
        """
        This function clears the singleton instances of the given class.
        Args:
            cls: The class whose singleton instance are to be cleared.
        """
        cls._instances = {}


class LoopIterators(metaclass=SingletonMeta):
    """
    This is a singleton class to implicitly providing the loop iterators.
    """

    def __init__(self):
        self.listsOfLoopIterators: list[PipelineIteratedValue] = []
        self.iterator: PipelineIteratedValue = None

    def register_new_iterator_list(self, iterator_list: Iterable[Any], deep_copy: bool = False):
        """
        This function is called, if the element of the list will be used as iterator values in a subsequent loop.
        Args:
            iterator_list:  the list of the iterator values.
            deep_copy:      if it is true the value of the elements of the list will be copied as well
                            (not only their references).

        """
        if deep_copy:
            iterator_list = copy.deepcopy(iterator_list)

        self.listsOfLoopIterators.append([PipelineIteratedValue(v, i) for i, v in enumerate(iterator_list)])

    def size_of_an_iterator_list(self, index: int) -> int:
        """
        It returns the size of the corresponding registered list of loop iterator values.
        Args:
            index: This is the index of the list (in the order of registration).

        Returns: length of the corresponding list.

        """
        if len(self.listsOfLoopIterators) < index:
            return 0
        else:
            # Corner case: if loop was never prepared, we pretend an empty list
            if len(self.listsOfLoopIterators) <= index:
                return 0
            return len(self.listsOfLoopIterators[index])

    def remove_an_iterator_list(self, index: int):
        """
        It removes the corresponding registered list of loop iterator values.
        Args:
            index: This is the index of the list (in the order of registration).
        """
        if len(self.listsOfLoopIterators) > index:
            del self.listsOfLoopIterators[index]

    def init_current_iterator(self, index: int):
        """
        It assigns the next value for variable self.iterator
        from the corresponding registered list of loop iterator values.
        Args:
            index: This is the index of the list (in the order of registration).
        """
        if len(self.listsOfLoopIterators) > index and len(self.listsOfLoopIterators[index]) > 0:
            self.iterator = self.listsOfLoopIterators[index].pop(0)

    def is_iterated_value_available(self) -> bool:
        """
        It returns true if the iterated value is still available and can be consumed with `pop_iterated_value`.
        """
        return self.iterator is not None

    def pop_iterated_value(self) -> Optional[PipelineIteratedValue]:
        """
        It returns the value of the variable self.iterator. The self.iterator is set to 'None'.

        Note: If `pop_iterator` returns None, the function is not called within a loop.
        """
        iterator = self.iterator
        self.iterator = None
        return iterator

    def pop_iterator(self) -> Any:
        """
        It returns the value of the variable self.iterator.value. The self.iterator is set to 'None'.

        Note: Don't use this function. You cannot discriminate against the iterator not being available
        and the actual iterated value to be falsy. Use `pop_iterated_value` instead.
        """
        iterator = self.pop_iterated_value()
        return iterator.value if iterator else None


class Arguments(metaclass=SingletonMeta):
    """
    This is a singleton class to implicitly providing function arguments given in the yaml configuration.
    """

    def __init__(self):
        self.current_param_lists = None
        self.buffered_param_lists = []
        self.buffered_dept_at_recursion = []
        self.param_lists_of_loops = None
        self.current_dept = 0
        self.max_dept = 0

    def get_upcoming_arguments(self, caller_name: str) -> dict[str, JSONType] | None:
        """
        It provides the upcoming yaml arguments for the function whose name is given as argument.
        Args:
            caller_name: name of the function, whose upcoming arguments will be return.

        Returns:
            A dictionary were the keys are the arguments name specified in the yaml configuration and the values are
            the values of the given arguments.
        """
        ret_val = None
        while self.current_param_lists and (not ret_val or caller_name not in ret_val):
            ret_val = self.current_param_lists.pop(0)
        if caller_name in ret_val:
            if ret_val[caller_name] and type(ret_val[caller_name]) is list:
                return ret_val[caller_name][0]
            else:
                return None
        else:
            return None

    def overwrite_current_depth(self, new_value: int):
        # This function is called only in case of recursion.
        # In this case the parameter queue (as well as the queue the pipeline of the loop kernel)
        # contains an extra entry (the data of the entry point of the recursion or in other words
        # the first recursively called loop kernel), that is why max_dept must be greater with 1.
        if self.current_dept + 1 > self.max_dept:
            self.max_dept = self.current_dept + 1
        self.buffered_dept_at_recursion.append(self.current_dept)
        self.current_dept = new_value

    def replace_current_argument_lists(self):
        """
        The arguments for loop kernel are stored in independent lists.
        If the execution a loop kernel is started, then parent list
        (belonging to the main list or a containing loop kernel) will be buffered and the subsequent
        list will be activated.
        """
        self.buffered_param_lists.append(self.current_param_lists)
        self.current_param_lists = self.param_lists_of_loops[self.current_dept].copy()
        self.current_dept += 1
        if self.current_dept > self.max_dept:
            self.max_dept = self.current_dept

    def renew_loop_argument_lists(self):
        """
        At each execution of a loop kernel, the list of arguments of its functions must be reinitialized.
        This is done by this function.
        """
        if self.current_dept - 1 > 0:
            self.current_param_lists = self.param_lists_of_loops[self.current_dept - 1].copy()
        else:
            self.current_param_lists = self.param_lists_of_loops[0].copy()

    def restore_last_buffered_argument_list(self):
        """
        If the execution returns to the main pipeline or the pipeline of the containing loop kernel, its buffered
        parameter list is re-activated.
        """
        self.current_param_lists = self.buffered_param_lists.pop()
        if len(self.buffered_dept_at_recursion) > 0:
            self.current_dept = self.buffered_dept_at_recursion.pop()
        else:
            self.current_dept -= 1
        if self.current_dept == 0:
            del self.param_lists_of_loops[: self.max_dept]
            self.max_dept = 0
