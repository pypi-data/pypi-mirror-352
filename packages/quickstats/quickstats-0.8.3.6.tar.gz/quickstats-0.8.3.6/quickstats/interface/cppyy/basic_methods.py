from typing import Dict
import cppyy

def get_std_object_map(source:Dict, typename:str):
    std = cppyy.gbl.std
    object_map = std.map(f"string, {typename}*")()
    object_map.keepalive = list()
    for key, obj in source.items():
        object_map.keepalive.append(obj)
        object_map.insert(object_map.begin(), std.pair(f"const string, {typename}*")(key, obj))
    return object_map