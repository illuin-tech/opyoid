from typing import List, Optional, Type, Union

from opyoid.exceptions import BindingError
from opyoid.provider import Provider
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import EMPTY, InjectedT
from .binding import Binding
from .binding_registry import BindingRegistry
from .class_binding import ClassBinding
from .instance_binding import InstanceBinding
from .multi_binding import ItemBinding, MultiBinding
from .provider_binding import ProviderBinding
from .registered_binding import RegisteredBinding
from .registered_multi_binding import RegisteredMultiBinding
from .self_binding import SelfBinding


class AbstractModule:
    """Base class for Modules, should not be used outside of the library."""

    def __init__(self, log_bindings: bool = False):
        self._is_configured = False
        self._binding_registry = BindingRegistry(log_bindings)

    @property
    def binding_registry(self) -> BindingRegistry:
        return self._binding_registry

    def __repr__(self) -> str:
        return ".".join([self.__class__.__module__, self.__class__.__qualname__])

    def configure(self) -> None:
        """Contains all bindings, called at injector initialization.

        Should not be called directly, but through configure_once.
        Only public to have a simpler API.
        """
        raise NotImplementedError

    def install(self, module: "AbstractModule") -> None:
        """Adds bindings from another Module to this one."""
        # pylint: disable=import-outside-toplevel
        from .private_module import PrivateModule

        module.configure_once()
        for binding in module.binding_registry.get_bindings_by_target().values():
            if isinstance(module, PrivateModule):
                if not module.is_exposed(binding.target):
                    continue
                if isinstance(binding, RegisteredMultiBinding):
                    binding = RegisteredMultiBinding(
                        binding.raw_binding,
                        item_bindings=[
                            RegisteredBinding(
                                registered_item_binding.raw_binding,
                                (module,) + binding.source_path,
                            )
                            for registered_item_binding in binding.item_bindings
                        ],
                    )
                else:
                    binding = RegisteredBinding(
                        binding.raw_binding,
                        (module,) + binding.source_path,
                    )
            self._binding_registry.register(binding, add_self_binding=False)

    # pylint: disable=too-many-arguments
    def bind(self,
             target_type: Type[InjectedT],
             to_class: Type[InjectedT] = EMPTY,
             to_instance: InjectedT = EMPTY,
             to_provider: Union[Provider, Type[Provider]] = EMPTY,
             scope: Type[Scope] = SingletonScope,
             named: Optional[str] = None) -> RegisteredBinding:
        try:
            binding = self._create_binding(
                target_type,
                to_class,
                to_instance,
                to_provider,
                scope,
                named,
            )
        except BindingError as error:
            raise BindingError(f"Error in {self!r} when binding to {target_type!r}: {error}") from None
        registered_binding = self._register(binding)
        return registered_binding

    def configure_once(self):
        """Calls configure if it has not already been called."""

        if not self._is_configured:
            self._is_configured = True
            self.configure()

    def multi_bind(self,
                   item_target_type: Type[InjectedT],
                   item_bindings: List[ItemBinding[InjectedT]],
                   scope: Type[Scope] = SingletonScope,
                   named: Optional[str] = None,
                   override_bindings: bool = True) -> RegisteredBinding:

        return self._register_multi_binding(
            MultiBinding(item_target_type, item_bindings, scope, named, override_bindings)
        )

    @staticmethod
    def bind_item(to_class: Type[InjectedT] = EMPTY,
                  to_instance: InjectedT = EMPTY,
                  to_provider: Union[Provider, Type[Provider]] = EMPTY) -> ItemBinding[InjectedT]:
        return ItemBinding(to_class, to_instance, to_provider)

    @staticmethod
    def _create_binding(target_type: Type[InjectedT],
                        bound_type: Type[InjectedT],
                        bound_instance: InjectedT,
                        bound_provider: Union[Provider, Type[Provider]],
                        scope: Type[Scope],
                        named: Optional[str]) -> Binding:
        if bound_instance is not EMPTY:
            return InstanceBinding(target_type, bound_instance, named)
        if bound_provider is not EMPTY:
            return ProviderBinding(target_type, bound_provider, scope, named)
        if bound_type is not EMPTY and bound_type != target_type:
            return ClassBinding(target_type, bound_type, scope, named)
        return SelfBinding(target_type, scope, named)

    def _register(self, binding: Binding[InjectedT]) -> RegisteredBinding:
        if isinstance(binding, MultiBinding):
            registered_binding = self._register_multi_binding(binding)
        else:
            registered_binding = RegisteredBinding(binding)
            self._binding_registry.register(registered_binding)
        return registered_binding

    def _register_multi_binding(self, binding: MultiBinding[InjectedT]) -> RegisteredMultiBinding:
        registered_binding = RegisteredMultiBinding(binding)
        for item_binding in binding.item_bindings:
            if item_binding.bound_type is not EMPTY:
                item_binding = SelfBinding(
                    item_binding.bound_type,
                    binding.scope,
                    binding.named,
                )
            elif item_binding.bound_instance is not EMPTY:
                item_binding = InstanceBinding(
                    binding.item_target_type,
                    item_binding.bound_instance,
                    binding.named,
                )
            elif item_binding.bound_provider is not EMPTY:
                item_binding = ProviderBinding(
                    binding.item_target_type,
                    item_binding.bound_provider,
                    binding.scope,
                    binding.named,
                )
            else:
                raise BindingError(
                    f"ItemBinding in {binding!r} has no instance, class or provider, one should be set")

            # pylint: disable=no-member
            registered_binding.item_bindings.append(RegisteredBinding(item_binding))
        self._binding_registry.register(registered_binding)
        return registered_binding
