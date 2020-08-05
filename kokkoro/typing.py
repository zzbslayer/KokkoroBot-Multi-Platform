from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple, Union

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider