from typing import Dict, Optional, TYPE_CHECKING

import attr

from .provider_registry import ProviderRegistry

if TYPE_CHECKING:
    from .bindings import AbstractBindingSpec
    from .providers import ProviderCreator
    from .bindings import BindingRegistry


@attr.s(auto_attribs=True)
class InjectionState:
    provider_creator: "ProviderCreator"
    binding_registry: "BindingRegistry"
    parent_state: Optional["InjectionState"] = None
    provider_registry: ProviderRegistry = attr.Factory(ProviderRegistry)
    state_by_binding_spec: Dict["AbstractBindingSpec", "InjectionState"] = attr.Factory(dict)
