import os
import uuid
import traceback
from typing import Optional, Union, Dict, List, Any, Iterable, Callable, Type
from itertools import repeat
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed
)

from quickstats import AbstractObject, GeneralEnum, timer
from quickstats.utils.common_utils import is_valid_file
from quickstats.core.typing import MISSING, MISSING_TYPE
from .logging import redirect_log
from ._base import ArgStore

class CacheState(GeneralEnum):
    NOCACHE = "NOCACHE"
    SUCCESS = "SUCCESS"
    BROKEN = "BROKEN"
    MISSING = "MISSING"
    ERROR = "ERROR"

class TaskState(GeneralEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"

class TaskFuture:

    def __init__(self, taskid: str, workid: Optional[int] = None):
        self._state = TaskState.PENDING
        self._taskid = taskid
        self._workid = workid
        self._result = MISSING
        self._exception = None

    def set_result(self, result: Any) -> None:
        if self._state in {TaskState.FINISHED, TaskState.FAILED}:
            raise RuntimeError(f'(TaskID = {self._taskid}, WorkID = {self._workidd}) '
                               f'Invalid state: {self._state}')
        self._result = result
        self._state = TaskState.FINISHED

    def set_exception(self, exception) -> None:
        if self._state in {TaskState.FINISHED, TaskState.FAILED}:
            raise RuntimeError(f'(TaskID = {self._taskid}, WorkID = {self._workid}) '
                               f'Invalid state: {self._state}')
        self._state = TaskState.FAILED
        self._exception = exception
        
    def has_result(self) -> bool:
        return not isinstance(self._result, MISSING_TYPE)

def _get_task_fn_wrapper(task):
    if not callable(task):
        raise ValueError('`task` must be callable')
    if issubclass(task, BaseTask):
        def fn(taskid, workid, args, kwargs, metadata):
            return task(args, kwargs, metadata)._run()
    else:
        def fn(taskid, workid, args, kwargs, metadata):
            future = TaskFuture(taskid, workid)
            try:
                result = task(*args, **kwargs)
            except Exception as exc:
                future.set_exception(exc)
            else:
                future.set_result(result)
            return future
    return fn

{future : taskid}
        
# BatchTask ?
class BaseTask(AbstractObject):

    abc = Parameter(...)

    @property
    def cache_output(self):
        ...

    @property
    def retry_count(self):
        ...

    @property
    def stdout(self):
        ...

    @classmethod
    def get_namespace(cls):
        return None

    @classmethod
    def get_label(cls):
        if not cls.get_namespace():
            return cls.__name__
        return f"{cls.get_namespace()}.{cls.__name__}"

    # > parameters (must be named) : do not allow args
    # > check param list for reserved parameters
    

    def __init__(self, *args, **kwargs):

        params = self.get_params()
        param_values = self.get_param_values(params, args, kwargs)

        # Set all values on class instance
        for key, value in param_values:
            setattr(self, key, value)
            
        self.taskid = taskid
        self.args = args
        self.kwargs = kwargs
        self.metadata = metadata

    @classmethod
    def generate_inputs(cls, task_input:Dict) -> InputIterator:
        return InputIterator(**task_config)

    def get_log_file(self) -> str:
        taskid = self.taskid
        workid = self.workid
        return f"task-{taskid}-{workid}.log"

    def get_cache_files(self) -> Optional[List[str]]:
        return None

    def cache_result(self) -> Any:
        return None

    def is_valid_cache(self, result: Any) -> bool:
        return True

    def _cache_result(self, future) -> CacheState:
        try:
            cache_files = self.get_cache_files()
            if not cache_files:
                return CacheState.NOCACHE
            if not all(is_valid_file(file) for file in cache_files):
                return CacheState.MISSING
            cached_result = self.cache_result()
            if not self.is_valid_cache(cached_result):
                return CacheState.BROKEN
            future.set_result(cached_result)
            return CacheState.SUCCESS
        except Exception as exc:
            traceback_msg = traceback.format_exc()
            future.set_exception(exc)
        return CacheState.ERROR

    def run(self) -> Any:
        raise NotImplementedError

    def enter(self):
        pass

    def exit(self, result: Any):
        pass

    def _run(self) -> TaskFuture:
        future = TaskFuture(self.taskid, self.workid)
        try:
            self.entry()
            if self.metadata.cache:
                status = self._cache_result(future)
                cache_files = self.get_cache_files()
                if status == CacheStatus.SUCCESS:
                    self.stdout.info(f'Cached output from {", ".join(cache_files)}.')
                    return future
                if status == CacheStatus.BROKEN:
                    self.stdout.info(f'Broken cache: {", ".join(cache_files)}. Retrying.')
                elif status == CacheStatus.ERROR:
                    self.stdout.info(f'An error has occurred while loading the cache: {", ".join(cache_files)}. Retrying.')

            log_path = self.get_log_file(config) if self.metadata.redirect_log else None
            with redirect_log(log_path):
                result = self.run(*self.args, **self.kwargs)
                
            self.exit(result)
        except Exception as exc:
            future.set_exception(exc)
        else:
            future.set_result(result)
        return future


class BatchedTask(BaseTask):

    ...

