import os
import sys
from ..file import read_text
from ..sys import sys_paths_relative
from .tools import find_venv_path
from .constants import venv_this


def activate_venv(rootdir=None, ignore=False):
    path_venv = find_venv_path(rootdir)
    path_scripts = sys_paths_relative(path_venv)['scripts']
    this_file = os.path.join(path_scripts, venv_this)
    if not ignore or os.path.isfile(this_file):
        exec(read_text(this_file), {'__file__': this_file})


def is_venv_active(prefix=None):
    return (prefix or sys.prefix) != sys.base_prefix
