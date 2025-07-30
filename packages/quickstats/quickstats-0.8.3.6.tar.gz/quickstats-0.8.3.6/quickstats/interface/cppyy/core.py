from typing import Optional, Any

import cppyy

def cpp_define(expression:str, name:Optional[str]=None):
    if name is None:
        hash_str = str(hash(expression)).replace("-", "n")
        name_guard = f"__cppyy_declare_{hash_str}__"
    else:
        name_guard = f"__cppyy_declare_{name}__"
    guarded_definition = f"#ifndef {name_guard}\n"
    guarded_definition += f"#define {name_guard}\n"
    guarded_definition += f"\n{expression}\n\n#endif\n"
    status = cppyy.cppdef(guarded_definition)
    return status

def addressof(obj: Any):
    return cppyy.ll.addressof(obj)

def is_null_ptr(obj: Any):
    return addressof(obj) == 0