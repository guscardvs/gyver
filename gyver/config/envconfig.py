import os
from pathlib import Path
from typing import Sequence
from typing import Union

from gyver.attrs import call_init
from gyver.attrs import define
from gyver.attrs import info

from gyver import utils

from .config import Config
from .config import EnvMapping
from .config import default_mapping
from .typedef import Env


@define
class DotFile:
    filename: Union[str, Path] = info(order=False)
    env: Env = info(order=lambda env: env.weight)
    apply_to_lower: bool = info(default=False, order=False)

    def is_higher(self, env: Env) -> bool:
        return self.env.weight >= env.weight


@define
class EnvConfig(Config):
    mapping: EnvMapping = default_mapping
    env_var: str = "CONFIG_ENV"
    dotfiles: Sequence[DotFile] = ()

    def __init__(
        self,
        *dotfiles: DotFile,
        env_var: str = "CONFIG_ENV",
        mapping: EnvMapping = default_mapping
    ) -> None:
        call_init(
            self,
            env_var=env_var,
            mapping=mapping,
            dotfiles=dotfiles,
        )

    def __post_init__(self):
        if self.dotfile:
            EnvConfig.file_values.manual_set(
                self, dict(self._read_file(self.dotfile.filename))
            )

    @utils.lazyfield
    def env(self):
        return self.__call__(self.env_var, Env.new)

    @utils.lazyfield
    def dotfile(self):
        """
        The dotfile function returns the dotfile object that is applicable to
        the current environment.  It traverses the list of dotfiles in reverse order,
        so that higher priority dotfiles are checked first.  If no matching dotfile is
        found, it returns None.

        :return: The first dotfile that is not higher than the current environment
        """

        for dot in sorted(self.dotfiles, reverse=True):
            if not dot.is_higher(self.env):
                break
            if dot.env != self.env and (
                not dot.apply_to_lower or not dot.is_higher(self.env)
            ):
                continue
            if not os.path.isfile(dot.filename):
                continue
            return dot
