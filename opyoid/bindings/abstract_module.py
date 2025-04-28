from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Type, Union

from opyoid.exceptions import BindingError
from opyoid.provider import Provider
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import EMPTY, InjectedT
from .binding import Binding
from .binding_registry import BindingRegistry
from .class_binding import ClassBinding
from .condition import Condition
from .instance_binding import InstanceBinding
from .multi_binding import ItemBinding, MultiBinding
from .provider_binding import ProviderBinding
from .registered_binding import RegisteredBinding
from .registered_multi_binding import RegisteredMultiBinding
from .self_binding import SelfBinding


class AbstractModule:
    """Base class for Modules, should not be used outside the library."""

    conditions: Tuple[Condition, ...] = ()

    def __init__(
        self,
        log_bindings: bool = False,
        shared_modules: Optional[Dict[Type["AbstractModule"], "AbstractModule"]] = None,
    ):
        self._is_configured = False
        self._binding_registry = BindingRegistry(log_bindings)
        self._module_instances = shared_modules if shared_modules is not None else {}

    @property
    def binding_registry(self) -> BindingRegistry:
        return self._binding_registry

    @classmethod
    def add_condition(cls, condition: Condition) -> None:
        cls.conditions = cls.conditions + (condition,)

    def __repr__(self) -> str:
        return ".".join([self.__class__.__module__, self.__class__.__qualname__])

    def configure(self) -> None:
        """Contains all bindings, called at injector initialization.

        Should not be called directly, but through configure_once.
        Only public to have a simpler API.
        """
        raise NotImplementedError

    def install(self, module: Union["AbstractModule", Type["AbstractModule"]]) -> None:
        """Adds bindings from another Module to this one."""
        # pylint: disable=import-outside-toplevel, cyclic-import
        from .private_module import PrivateModule

        module_instance = self._get_module_instance(module)

        module_instance.configure_once()
        for binding in module_instance.binding_registry.get_bindings_by_target().values():
            if isinstance(module_instance, PrivateModule):
                if not module_instance.is_exposed(binding.target):
                    continue
                if isinstance(binding, RegisteredMultiBinding):
                    binding = RegisteredMultiBinding(
                        binding.raw_binding,
                        module_instance,
                        item_bindings=[
                            RegisteredBinding(
                                registered_item_binding.raw_binding,
                                module_instance,
                                (module_instance,) + binding.source_path,
                            )
                            for registered_item_binding in binding.item_bindings
                        ],
                    )
                else:
                    binding = RegisteredBinding(
                        binding.raw_binding,
                        module_instance,
                        (module_instance,) + binding.source_path,
                    )
            self._binding_registry.register(binding, add_self_binding=False)

    # pylint: disable=too-many-arguments
    def bind(
        self,
        target_type: Any,
        *,
        to_class: Type[Any] = EMPTY,  # type: ignore[assignment]
        to_instance: Any = EMPTY,
        to_provider: Union[Provider[Any], Type[Provider[Any]], Callable[..., Any]] = EMPTY,  # type: ignore[assignment]
        scope: Type[Scope] = SingletonScope,
        named: Optional[str] = None,
    ) -> RegisteredBinding[InjectedT]:
        try:
            binding = self._create_binding(
                target_type=target_type,
                bound_class=to_class,
                bound_instance=to_instance,
                bound_provider=to_provider,
                scope=scope,
                named=named,
            )
        except BindingError as error:
            raise BindingError(f"Error in {self!r} when binding to {target_type!r}: {error}") from None
        registered_binding = self._register(binding)
        return registered_binding

    def configure_once(self) -> None:
        """Calls configure if it has not already been called."""

        if not self._is_configured:
            self._is_configured = True
            if all(condition.is_valid() for condition in self.conditions):
                self.configure()

    def multi_bind(
        self,
        item_target_type: Any,
        item_bindings: List[ItemBinding[Any]],
        *,
        scope: Type[Scope] = SingletonScope,
        named: Optional[str] = None,
        override_bindings: bool = False,
    ) -> RegisteredMultiBinding[Any]:
        return self._register_multi_binding(
            MultiBinding(
                item_target_type, item_bindings, scope=scope, named=named, override_bindings=override_bindings
            ),
        )

    @staticmethod
    def bind_item(
        *,
        to_class: Type[InjectedT] = EMPTY,  # type: ignore[assignment]
        to_instance: InjectedT = EMPTY,  # type: ignore[assignment]
        to_provider: Union[
            Provider[InjectedT],
            Type[Provider[InjectedT]],
            Callable[..., InjectedT],
        ] = EMPTY,  # type: ignore[assignment]
        scope: Type[Scope] = EMPTY,  # type: ignore[assignment]
        named: Optional[str] = EMPTY,  # type: ignore[assignment]
    ) -> ItemBinding[InjectedT]:
        return ItemBinding(
            bound_class=to_class, bound_instance=to_instance, bound_provider=to_provider, scope=scope, named=named
        )

    def _get_module_instance(self, module: Union["AbstractModule", Type["AbstractModule"]]) -> "AbstractModule":
        # pylint: disable=import-outside-toplevel
        from .private_module import PrivateModule

        if isinstance(module, AbstractModule):
            module_instance = module
        else:
            if module not in self._module_instances:
                if issubclass(module, PrivateModule):
                    self._module_instances[module] = module()
                else:
                    self._module_instances[module] = module(shared_modules=self._module_instances)
            module_instance = self._module_instances[module]
        return module_instance

    @staticmethod
    def _create_binding(
        *,
        target_type: Any,
        bound_class: Type[Any],
        bound_instance: Any,
        bound_provider: Union[Provider[Any], Type[Provider[Any]], Callable[..., Any]],
        scope: Type[Scope],
        named: Optional[str],
    ) -> Binding[Any]:
        if bound_instance is not EMPTY:
            return InstanceBinding(target_type, bound_instance, named=named)
        if bound_provider is not EMPTY:
            return ProviderBinding(target_type, bound_provider, scope=scope, named=named)
        if bound_class is not EMPTY and bound_class != target_type:
            return ClassBinding(target_type, bound_class, scope=scope, named=named)
        return SelfBinding(target_type, scope=scope, named=named)

    def _register(self, binding: Binding[Any]) -> RegisteredBinding[Any]:
        if isinstance(binding, MultiBinding):
            registered_binding: RegisteredBinding[Any] = self._register_multi_binding(binding)
        else:
            registered_binding = RegisteredBinding(binding, binding_source=self)
            self._binding_registry.register(registered_binding)
        return registered_binding

    def _register_multi_binding(self, binding: MultiBinding[InjectedT]) -> RegisteredMultiBinding[InjectedT]:
        registered_binding = RegisteredMultiBinding(binding, binding_source=self)
        for source_item_binding in binding.item_bindings:
            scope = cast(
                Type[Scope], source_item_binding.scope if source_item_binding.scope is not EMPTY else binding.scope
            )
            named = cast(
                Optional[str], source_item_binding.named if source_item_binding.named is not EMPTY else binding.named
            )
            if source_item_binding.bound_class is not EMPTY:
                item_binding: Binding[InjectedT] = SelfBinding(
                    cast(Type[InjectedT], source_item_binding.bound_class),
                    scope=scope,
                    named=named,
                )
            elif source_item_binding.bound_instance is not EMPTY:
                item_binding = InstanceBinding(
                    binding.item_target_type,
                    cast(InjectedT, source_item_binding.bound_instance),
                    named=named,
                )
            elif source_item_binding.bound_provider is not EMPTY:
                item_binding = ProviderBinding(
                    binding.item_target_type,
                    cast(
                        Union[Type[Provider[InjectedT]], Provider[InjectedT], Callable[..., InjectedT]],
                        source_item_binding.bound_provider,
                    ),
                    scope=scope,
                    named=named,
                )
            else:
                raise BindingError(f"ItemBinding in {binding!r} has no instance, class or provider, one should be set")

            registered_binding.item_bindings.append(RegisteredBinding(item_binding, binding_source=self))
        self._binding_registry.register(registered_binding)
        return registered_binding
