from typing import List, Optional, Type, Union

from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import EMPTY, InjectedT
from .binding import Binding
from .binding_registry import BindingRegistry
from .class_binding import ClassBinding
from .factory_binding import FactoryBinding
from .instance_binding import InstanceBinding
from .multi_binding import ItemBinding, MultiBinding
from .registered_binding import RegisteredBinding


class AbstractModule:
    """Base class for Modules, should not be used outside of the library."""

    def __init__(self):
        self._is_configured = False
        self._binding_registry = BindingRegistry()

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
            if isinstance(module, PrivateModule) and not module.is_exposed(binding):
                continue
            binding = RegisteredBinding(
                binding.raw_binding,
                (module,) + binding.source_path,
            )
            self._binding_registry.register(binding)

    # pylint: disable=too-many-arguments
    def bind(self,
             target_type: Type[InjectedT],
             to_class: Type[InjectedT] = EMPTY,
             to_instance: InjectedT = EMPTY,
             to_factory: Union[Factory, Type[Factory]] = EMPTY,
             scope: Type[Scope] = SingletonScope,
             annotation: Optional[str] = None) -> RegisteredBinding:
        if to_class is EMPTY and to_instance is EMPTY and to_factory is EMPTY:
            to_class = target_type
        try:
            binding = self._create_binding(
                target_type,
                to_class,
                to_instance,
                to_factory,
                scope,
                annotation,
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
                   annotation: Optional[str] = None,
                   override_bindings: bool = True) -> None:

        self._register(
            MultiBinding(item_target_type, item_bindings, scope, annotation, override_bindings)
        )

    @staticmethod
    def bind_item(to_class: Type[InjectedT] = EMPTY,
                  to_instance: InjectedT = EMPTY,
                  to_factory: Union[Factory, Type[Factory]] = EMPTY) -> ItemBinding[InjectedT]:
        return ItemBinding(to_class, to_instance, to_factory)

    @staticmethod
    def _create_binding(target_type: Type[InjectedT],
                        bound_type: Type[InjectedT],
                        bound_instance: InjectedT,
                        bound_factory: Union[Factory, Type[Factory]],
                        scope: Type[Scope],
                        annotation: Optional[str]) -> Binding:
        if bound_instance is not EMPTY:
            return InstanceBinding(target_type, bound_instance, annotation)
        if bound_factory is not EMPTY:
            return FactoryBinding(target_type, bound_factory, scope, annotation)
        return ClassBinding(target_type, bound_type, scope, annotation)

    def _register(self, binding: Binding[InjectedT]) -> RegisteredBinding:
        registered_binding = RegisteredBinding(binding)
        self._binding_registry.register(registered_binding)
        return registered_binding