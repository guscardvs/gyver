import os
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Sequence
from typing import Union

from gyver.attrs import call_init
from gyver.attrs import define
from gyver.attrs import info

from gyver import utils
from gyver.config.config import MISSING

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


def default_rule(_: Env):
    return False


@define
class EnvConfig(Config):
    mapping: EnvMapping = default_mapping
    env_var: str = "CONFIG_ENV"
    env_cast: Callable[[str], Env] = Env
    dotfiles: Sequence[DotFile] = ()
    ignore_default_rule: Callable[[Env], bool] = default_rule

    def __init__(
        self,
        *dotfiles: DotFile,
        env_var: str = "CONFIG_ENV",
        mapping: EnvMapping = default_mapping,
        ignore_default_rule: Callable[[Env], bool] = default_rule,
        env_cast: Callable[[str], Env] = Env
    ) -> None:
        call_init(
            self,
            env_var=env_var,
            mapping=mapping,
            dotfiles=dotfiles,
            ignore_default_rule=ignore_default_rule,
            env_cast=env_cast,
        )

    def __post_init__(self):
        if self.dotfile:
            EnvConfig.file_values.manual_set(
                self, dict(self._read_file(self.dotfile.filename))
            )

    @utils.lazyfield
    def env(self):
        return Config.get(self, self.env_var, Env.new)

    @utils.lazyfield
    def ignore_default(self):
        return self.ignore_default_rule(self.env)

    def get(
        self,
        name: str,
        cast: Callable[..., Any] = ...,
        default: Union[Any, type[MISSING]] = ...,
    ) -> Any:
        default = MISSING if self.ignore_default else default
        return Config.get(self, name, cast, default)

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
