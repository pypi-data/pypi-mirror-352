import os
from typing import Optional, Union, Dict, List, Any
from itertools import repeat
from functools import lru_cache
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed
)

from quickstats import AbstractObject, GeneralEnum, timer

class PoolType(GeneralEnum):
    THREAD = "thread"
    PROCESS = "process"

@lru_cache(maxsize=None)
def get_executor(pool_type: Union[str, PoolType]):
    pool_type = PoolType.parse(pool_type)
    if pool_type == PoolType.THREAD:
        return ThreadPoolExecutor
    elif pool_type == PoolType.PROCESS:
        return ProcessPoolExecutor
    raise ValueError(f'Unknown pool type: {pool_type}')

class BaseRunner(AbstractObject):

    def __init__(self,
                 retry: int = 0,
                 parallel: int = -1,
                 pool_type: str = 'process',
                 verbosity: str = 'INFO'):
        super().__init__(verbosity=verbosity)

        self.parallel = parallel
        self.pool_type = pool_type

    @property
    def pool_type(self) -> PoolType:
        return self._pool_type

    @pool_type.setter
    def pool_type(self, value: str) -> None:
        self._pool_type = PoolType.parse(value)
    
    def _sequential_run(self, task, task_input):
        outputs = []
        task_params = task.create_params(task_config)
        _metadata = task.create_metadata()
        for step, params in enumerate(task_params.next()):
            metadata = {**_metadata, 'stepid': step}
            output, taskid, stepid = task._run_step(params, metadata)
            outputs.append({
                'taskid': taskid,
                'stepid': stepid,
                'output': output
            })
        return outputs

    def _concurrent_run(self, task, task_input):
        if self.parallel == 0:
            return self._sequential_run(task, task_config)
        max_workers = os.cpu_count() if self.parallel < 0 else self.parallel
        executor_fn = get_executor(self.pool_type)
        outputs = []
        with executor_fn(max_workers) as executor:
            task_params = task._create_params(task_config)
            _metadata = task.create_metadata()
            futures = {}
            while futures:
                for step, params in enumerate(task_params.next()):
                    metadata = {**_metadata, 'stepid': step}
                    futures.append(executor.submit(task._run_step, params, metadata))
                for future in as_completed(futures):
                    output, taskid, stepid = future.result()
                    outputs.append({
                        'taskid': taskid,
                        'stepid': stepid,
                        'output': output
                    })
        return result
            
    def run_task(self, task: BaseTask, /, task_input: Any,
                 task_config: Dict) -> Any:
        with timer() as t:
            results = self._concurrent_run(task, task_config)
        self.stdout.info('Task (TaskID = ) has finished. Time Taken = ...s')