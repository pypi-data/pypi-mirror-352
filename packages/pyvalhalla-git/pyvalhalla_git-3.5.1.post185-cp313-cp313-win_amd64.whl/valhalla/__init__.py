"""""" # start delvewheel patch
def _delvewheel_patch_1_10_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_10_1()
del _delvewheel_patch_1_10_1
# end delvewheel patch

try:
    from ._valhalla import *
except ModuleNotFoundError:
    from _valhalla import *

from .actor import Actor
from .config import get_config, get_help
from .__version__ import __version__
