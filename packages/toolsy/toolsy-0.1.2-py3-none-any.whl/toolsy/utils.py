import os
import sys
from pathlib import Path


def get_HOME() -> Path:
    """
    obtain HOME directory
    """
    if sys.platform == 'win32':
        home_dir = os.environ['USERPROFILE']
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        home_dir = os.environ['HOME']
    else:
        raise NotImplemented(f"Can't identify the HOME directory of {sys.platform} platform!")
    return Path(home_dir)
