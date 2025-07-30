from typing import Optional
from functools import lru_cache
import os
import multiprocessing

import httpx
from servicex import ServiceXClient
from servicex.query_cache import QueryCache
from servicex.configuration import Configuration
from tinydb.table import Table

__all__ = ["servicex_config"]

servicex_lock = multiprocessing.Lock()

def thread_safe(func):
    """Wrap a function to ensure it's executed in a thread-safe manner."""
    def wrapper(*args, **kwargs):
        with servicex_lock:
            return func(*args, **kwargs)
    return wrapper

class ServiceXConfig:
    """Manage configuration patches and settings for ServiceX."""
    
    def __init__(self):
        self.cache_path = None
        self.timeout = None

    @lru_cache(maxsize=1)
    def patch_cache_path(self, undo:bool=False):

        if undo and hasattr(Configuration, "_original_add_from_path"):
            Configuration._add_from_path = Configuration._original_add_from_path
            return None
        # backup original definition
        if not hasattr(Configuration, "_original_add_from_path"):
            Configuration._original_add_from_path = Configuration._add_from_path
        
        def wrapper(cls, *args, **kwargs):
            yaml_config = cls._original_add_from_path(*args, **kwargs)
            if self.cache_path is not None:
                yaml_config['cache_path'] = self.cache_path
            return yaml_config
    
        Configuration._add_from_path = classmethod(wrapper)

    @lru_cache(maxsize=1)
    def patch_async_client_timeout(self, undo:bool=False):
    
        if undo and hasattr(httpx, "_AsyncClient"):
            httpx.AsyncClient = httpx._AsyncClient
            return None
        # backup original definition
        if not hasattr(httpx, '_AsyncClient'):
            httpx._AsyncClient = httpx.AsyncClient
    
        def wrapper(*args, **kwargs):
            if self.timeout is not None:
                return httpx._AsyncClient(*args, **kwargs,
                                          timeout=self.timeout)
            return httpx._AsyncClient(*args, **kwargs)
    
        # Patch with modified timeout settings
        httpx.AsyncClient = wrapper

    @lru_cache(maxsize=1)
    def patch_multiprocess_safety(self, undo:bool=False):

        servicex_attributes = ['get_code_generators']
        query_cache_attributes = ['cache_transform', 'update_record',
                                  'get_transform_by_hash', 'cached_queries',
                                  'get_transform_by_request_id']
    
        if undo:
            for attr in servicex_attributes:
                if hasattr(ServiceXClient, f'_{attr}'):
                    setattr(ServiceXClient, attr, getattr(ServiceXClient, f'_{attr}'))
            for attr in query_cache_attributes:
                if hasattr(QueryCache, f'_{attr}'):
                    setattr(QueryCache, attr, getattr(QueryCache, f'_{attr}'))
            if hasattr(Table, "_original_get_next_id"):
                Table._get_next_id = Table._original_get_next_id
                return None
                
        for attr in servicex_attributes:
            if not hasattr(ServiceXClient, f'_{attr}'):
                setattr(ServiceXClient, f'_{attr}', getattr(ServiceXClient, attr))
            setattr(ServiceXClient, attr, thread_safe(getattr(ServiceXClient, f'_{attr}')))
    
        for attr in query_cache_attributes:
            if not hasattr(QueryCache, f'_{attr}'):
                setattr(QueryCache, f'_{attr}', getattr(QueryCache, attr))
            setattr(QueryCache, attr, thread_safe(getattr(QueryCache, f'_{attr}')))
    
        if not hasattr(Table, '_original_get_next_id'):
            Table._original_get_next_id = Table._get_next_id
            
        def get_next_id_wrapper(self_, *args, **kwargs):
            self_._next_id = None
            return self_._original_get_next_id(*args, **kwargs)
        Table._get_next_id = get_next_id_wrapper

    def patch_all(self):
        self.patch_cache_path()
        self.patch_async_client_timeout()
        self.patch_multiprocess_safety()

    def unpatch_all(self):
        self.patch_cache_path(undo=True)
        self.patch_async_client_timeout(undo=True)
        self.patch_multiprocess_safety(undo=True)

    def set_cache_path(self, path:str):
        self.patch_cache_path()
        self.cache_path = path

    def set_timeout(self, timeout: Optional[float]=None,
                    connect: Optional[float]=None,
                    read: Optional[float]=None,
                    write: Optional[float]=None,
                    pool: Optional[float]=None):
        self.patch_async_client_timeout()
        timeout_spec = {k: v for k, v in [('connect', connect), 
                                          ('read', read),
                                          ('write', write),
                                          ('pool', pool)] if v is not None}
        timeout = httpx.Timeout(timeout, **timeout_spec)
        self.timeout = timeout

    def get_cache_db_path(self, cache_path:Optional[str]=None):
        cache_path = cache_path or self.cache_path or None
        if cache_path is None:
            return None
        cache_db_path = os.path.join(cache_path, "db.json")
        if not os.path.exists(cache_db_path):
            return None
        return cache_db_path

servicex_config = ServiceXConfig()