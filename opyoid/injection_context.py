import logging
from inspect import Parameter
from typing import Any, Generic, List, Optional, Type, TYPE_CHECKING, TypeVar

import attr

from .exceptions import CyclicDependencyError
from .provider import Provider
from .target import Target
from .utils import InjectedT

if TYPE_CHECKING:
    from .bindings import RegisteredBinding
    from .injection_state import InjectionState


InjectedSubT = TypeVar("InjectedSubT", bound=Any)


@attr.s(auto_attribs=True)
class InjectionContext(Generic[InjectedT]):
    logger = logging.getLogger(__name__)

    target: Target[InjectedT]
    injection_state: "InjectionState"
    parent_context: Optional["InjectionContext[Any]"] = attr.ib(default=None, eq=False)
    allow_jit_provider: bool = True
    current_class: Optional[Type[InjectedT]] = None
    current_parameter: Optional[Parameter] = None

    def __attrs_post_init__(self) -> None:
        context = self
        while context.parent_context:
            if self == context.parent_context:
                dependency_chain = "\n".join(f"-> {target!r}" for target in reversed(self._dependency_chain))
                self.logger.error(f"Cyclic dependency detected, injection graph: \n{dependency_chain}")
                raise CyclicDependencyError(f"Cyclic dependency detected, injection graph: \n{dependency_chain}")
            context = context.parent_context

    @property
    def _dependency_chain(self) -> List[Target[Any]]:
        context = self
        chain = [self.target]
        while context.parent_context:
            context = context.parent_context
            chain.append(context.target)
        return chain

    def get_child_context(
        self,
        new_target: Target[InjectedSubT],
        *,
        allow_jit_provider: bool = True,
        current_class: Optional[Type[InjectedSubT]] = None,
        current_parameter: Optional[Parameter] = None,
    ) -> "InjectionContext[InjectedSubT]":
        return InjectionContext(
            new_target, self.injection_state, self, allow_jit_provider, current_class, current_parameter
        )

    def get_new_state_context(self, new_state: "InjectionState") -> "InjectionContext[InjectedT]":
        return InjectionContext(self.target, new_state, self.parent_context, self.allow_jit_provider)

    def get_provider(self) -> Provider[InjectedT]:
        return self.injection_state.provider_creator.get_provider(self)

    def has_binding(self) -> bool:
        return self.target in self.injection_state.binding_registry

    def get_binding(self) -> Optional["RegisteredBinding[InjectedT]"]:
        return self.injection_state.binding_registry.get_binding(self.target)
