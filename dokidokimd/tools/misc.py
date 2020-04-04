import os
import re
import sys
from types import ModuleType, FunctionType

from gc import get_referents

BLACKLIST = type, ModuleType, FunctionType


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


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


PATH_SAFE_REGEX = r"[^a-zA-Z0-9_\- \+,%\(\)\[\]\{\}'~@]+"
PATH_SAFE_REPLACE_CHAR = r'_'
COMPILED_PATH_SAFE_REGEX = re.compile(PATH_SAFE_REGEX, re.UNICODE)


def make_path_os_safe(unsafe_path, substitute_char=PATH_SAFE_REPLACE_CHAR):
    return COMPILED_PATH_SAFE_REGEX.sub(substitute_char, unsafe_path)
