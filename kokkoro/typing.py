from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Set, Tuple, Union

from PIL import Image
from matplotlib.figure import Figure

def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider