from pathlib import Path
from typing import Any
from typing import Optional
from typing import Sequence
from typing import TypeVar

from pydantic.fields import ModelField

from gyver.config.adapter.factory import AdapterConfigFactory
from gyver.config.adapter.mark import mark
from gyver.config.adapter.pydantic import PydanticResolverStrategy
from gyver.model import Model
from gyver.utils import finder
from gyver.utils.helpers import DeprecatedClass
from gyver.utils.helpers import deprecated

from .config import Config


@mark
class ProviderConfig(Model):
    __prefix__ = ""
    __without_prefix__ = ()

    class Config:
        alias_generator = str.upper
        fields = {"exclude": {}}


ProviderT = TypeVar("ProviderT", bound=ProviderConfig)

_default_config = Config()


@deprecated
def from_config(
    provider: type[ProviderT],
    *,
    __config__: Config = _default_config,
    **presets: Any,
) -> ProviderT:
    return ConfigLoader(__config__).load(provider, **presets)


class ConfigLoader(DeprecatedClass):
    def __init__(
        self,
        config: Config = _default_config,
        prefix: Optional[str] = None,
        without_prefix: Sequence[str] = (),
    ):
        super().__init__()
        self._adapter_factory = AdapterConfigFactory(config)
        self._prefix = prefix
        self._without_prefix = without_prefix

    def load(self, model_cls: type[ProviderT], **presets: Any) -> ProviderT:
        return self._adapter_factory.load(
            model_cls, __prefix__=self._prefix or "", presets=presets
        )

    def resolve_names(
        self, model_cls: type[ProviderConfig], field: ModelField
    ) -> Sequence[str]:
        return self._adapter_factory.resolve_names(
            model_cls, PydanticResolverStrategy(field), self._prefix or ""
        )

    @classmethod
    def resolve_confignames(
        cls,
        root: Path,
    ) -> dict[type[ProviderConfig], tuple[Sequence[str], ...]]:
        """
        The resolve_confignames function resolves the names of all environment
        variables required by the configs in
        a ProviderConfig subclass.
        It returns them in a dict of {class: (configs)}.

        :param cls: Call the class_validator function, which is used to validate that a
        class has all of the required attributes
        :param root: Path: Specify the root directory of the project
        :return: A dictionary of {class: (configs)}
        """

        validator = finder.class_validator(ProviderConfig)
        provider_finder = finder.Finder(validator, root)
        provider_finder.find()
        tempself = cls()
        return {
            provider: tuple(
                tempself.resolve_names(provider, field)
                for field in provider.__fields__.values()
            )
            for provider in provider_finder.output.values()
        }
