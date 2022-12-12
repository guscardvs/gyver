import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from gyver import utils

from .config import Config
from .config import EnvMapping
from .config import default_mapping
from .typedef import Env


@dataclass(frozen=True)
class DotFile:
    filename: Union[str, Path]
    env: Env
    apply_to_lower: bool = False

    def __gt__(self, other: "DotFile") -> bool:
        return self.env.weight > other.env.weight

    def is_higher(self, env: Env) -> bool:
        return self.env.weight >= env.weight


class EnvConfig(Config):
    def __init__(
        self,
        *dotfiles: DotFile,
        env_var: str = "CONFIG_ENV",
        mapping: EnvMapping = default_mapping
    ) -> None:
        self._env_var = env_var
        self._dotfiles = dotfiles
        self._mapping = mapping
        self._file_values = {}
        if self.dotfile:
            self._read_file(self.dotfile.filename)

    @utils.lazyfield
    def env(self):
        return self.__call__(self._env_var, Env.new)

    @utils.lazyfield
    def dotfile(self):
        for dot in sorted(self._dotfiles, reverse=True):
            if not dot.is_higher(self.env):
                break
            if dot.env != self.env and (
                not dot.apply_to_lower or not dot.is_higher(self.env)
            ):
                continue
            if not os.path.isfile(dot.filename):
                continue
            return dot
