import os
from .constants import venv_list, venv_config_file


def is_venv_path(path):
    return os.path.isfile(os.path.join(path, venv_config_file))


def find_venv_path(path=None):
    if not path:
        path = os.getcwd()
    for item in venv_list:
        result = os.path.join(path, item)
        if is_venv_path(result):
            return result
