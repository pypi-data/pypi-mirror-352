import os
from typing import Optional, Union, Dict, List, Any, Callable
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from quickstats import AbstractObject, GeneralEnum

from .base_task import BaseTask

class PoolType(GeneralEnum):
    THREAD = "thread"
    PROCESS = "process"

class ConcurrentTasks(AbstractObject):

    @property
    def pool_type(self) -> PoolType:
        return self._pool_type

    @pool_type.setter
    def pool_type(self, value: str) -> None:
        self._pool_type = PoolType.parse(value)
    
    def __init__(self, parallel: int = -1,
                 save_log: bool = True, cache: bool = True,
                 pool_type: str = 'process',
                 verbosity: Optional[Union[int, str]] = "INFO"):
        super().__init__(verbosity=verbosity)

        # Initialize attributes for managing tasks and configuration
        self.cache = cache
        self.parallel = parallel
        self.save_log = save_log
        self.pool_type = pool_type
        self.reset()  # Initialize tasks dictionary

    def reset(self):
        self.tasks = {}

    def add_task(self, name: str, task: BaseTask, **kwargs):
        if not isinstance(task, BaseTask):
            raise ValueError('`task` must be an instance of BaseTask')
        if name in self.tasks:
            self.stdout.warning(f'Task with name {name} already exists. Overriding.')
        self.tasks[name] = (task, kwargs)

    def execute(self):
        results = {}
        if self.parallel == 0:
            results = {}
            for name, (task, kwargs) in self.tasks.items():
                iterable = task.create_iterable(kwargs)
                results[name] = [task.execute(inputs) for inputs in iterable]
        if self.parallel == -1:
            max_workers = os.cpu_count()
        else:
            max_workers = self.parallel
        if pool_type == PoolType.THREAD:
            pool = ThreadPoolExecutor
        elif pool_type == PoolType.PROCESS:
            pool = ProcessPoolExecutor
        else:
            raise ValueError(f'Unknown pool type: {pool}')
        with pool(max_workers) as executor:
            futures = {}
            for name, (func, kwargs) in self.tasks.items():
                iterable = func.create_iterable(kwargs)
                futures[name] = [executor.submit(func.execute, inputs, self.cache) for inputs in iterable]
            results = {name: [future.result() for future in futures[name]] for name in futures}
        return results