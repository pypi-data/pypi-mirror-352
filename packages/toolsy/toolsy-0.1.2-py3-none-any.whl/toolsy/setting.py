import inspect
import json
import os
from pathlib import Path

from toolsy.utils import get_HOME

ComDir = os.path.dirname(os.path.abspath(os.path.realpath(inspect.getfile(inspect.currentframe()))))
RootDir = os.path.dirname(ComDir)
WorkDir = Path.cwd()
HomeDir = get_HOME()


class ConfigManager(object):

    def __init__(self):
        self.config_dir = None
        self.logdir = None

        self.load()

    def __repr__(self):
        return f"------------------------------------Configure Information--------------------------------- \n" \
               f"! ConfigDir:      {self.config_dir} \n" \
               f"! LogDir:         {self.logdir} \n" \
               f"------------------------------------------------------------------------------------------"

    def load(self):
        """
        Load the configuration (need consider the multi-users)
        """
        # check config.json, if not exist, `config set to {}`
        try:
            with open(f"{RootDir}/config.json", "r") as f:
                config = json.load(f)
        except (NotADirectoryError, FileNotFoundError):
            config = {}

        # check config_dir, if not specify this key, set to RootDir
        try:
            self.config_dir = Path(config['config_dir'])  # config directory
        except KeyError:
            self.config_dir = Path(RootDir)

        # specify the logdir, if not exist, set to HomeDir/logs
        try:
            if Path(config['logdir']).exists():
                self.logdir = Path(config['logdir'])  # location of logdir
            else:
                self.logdir = HomeDir / "logs"
        except KeyError:
            self.logdir = HomeDir / "logs"


if __name__ == '__main__':
    config = ConfigManager()
    print()
