import sys
from gc import get_referents
from types import ModuleType, FunctionType

BLACKLIST = type, ModuleType, FunctionType


def get_object_mem_size(obj):
    """
    Credit to Aaron Hall
    """
    if isinstance(obj, BLACKLIST):
        raise TypeError(F'getsize() does not take argument of type: {type(obj)}')
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size
