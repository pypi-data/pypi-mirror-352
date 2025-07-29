from contextlib import contextmanager
from genericpath import exists
import os
from pathlib import Path
import pathlib
from typing import Any
import yaml

_config: Any = {}

try:
    with open(os.getenv('STACK_CONFIG_PATH', '/etc/stack/config.yml')) as config_file:
        _config = yaml.safe_load(config_file) or {}
except:
    pass

def stacks_path():
    return Path(('stacks_path' in _config and _config['stacks_path']) or '/etc/stack/stacks')

def stack_path(name: str):
    return stacks_path().joinpath(name)

def stack_exists(name: str):
    return exists(stack_path(name))

@contextmanager
def stack(name: str):
    cwd = os.curdir
    os.chdir(stack_path(name))
    yield
    os.chdir(cwd)