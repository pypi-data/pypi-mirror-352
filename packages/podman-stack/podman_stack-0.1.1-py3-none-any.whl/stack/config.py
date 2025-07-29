from contextlib import contextmanager
import os
from pathlib import Path
import pathlib
from typing import Any
import yaml

_config: Any

with open(os.getenv('STACK_CONFIG_PATH', '/etc/stack/config.yml')) as config_file:
    _config = yaml.load(config_file)

def stacks_path():
    return Path(_config.stacks_path or '/etc/stack/stacks')

@contextmanager
def stack(name: str):
    cwd = os.curdir
    os.chdir(stacks_path().joinpath(name))
    yield
    os.chdir(cwd)