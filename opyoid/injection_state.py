from typing import Dict, Optional, TYPE_CHECKING

import attr

from .bindings import AbstractModule, BindingRegistry
from .injector_options import InjectorOptions
from .provider_registry import ProviderRegistry

if TYPE_CHECKING:
    from .providers import ProviderCreator


@attr.s(auto_attribs=True)
class InjectionState:
    provider_creator: "ProviderCreator"
    binding_registry: BindingRegistry
    options: InjectorOptions = attr.Factory(InjectorOptions)
    parent_state: Optional["InjectionState"] = None
    provider_registry: ProviderRegistry = attr.Factory(ProviderRegistry)
    state_by_module: Dict[AbstractModule, "InjectionState"] = attr.Factory(dict)
