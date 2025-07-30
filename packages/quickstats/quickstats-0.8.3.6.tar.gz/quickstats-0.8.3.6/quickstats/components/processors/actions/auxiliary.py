from quickstats import GeneralEnum

class RooProcReturnCode(GeneralEnum):
    NORMAL     = 0
    SKIP_CHILD = 1

ACTION_MAP = dict()

def get_action(action_name:str):
    return ACTION_MAP.get(action_name, None)

def register_action(action_cls):
    name = action_cls.NAME
    if (name is not None) and (name not in ACTION_MAP):
        ACTION_MAP[name] = action_cls
    return action_cls