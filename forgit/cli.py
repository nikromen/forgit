from pathlib import Path
from typing import Optional

from forgit.config import ConfigSchema, Config


def _get_config(config_file_path: Optional[Path]) -> ConfigSchema:
    config_cls = Config(config_file_path) if config_file_path is not None else Config()
    return config_cls.get_config()
