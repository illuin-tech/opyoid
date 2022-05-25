from typing import Callable, Dict, List, Optional, TYPE_CHECKING, Tuple, Type, Union

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

if TYPE_CHECKING:
    from typing import TypeVar


class AbstractModule:
    """Base class for Modules, should not be used outside of the library."""

    conditions: Tuple[Condition, ...] = ()

    def __init__(
        self, log_bindings: bool = False, shared_modules: Dict[Type["AbstractModule"], "AbstractModule"] = None
    ):
        self._is_configured = False
        self._binding_registry = BindingRegistry(log_bindings)
        self._module_instances = shared_modules or {}

    @property
    def binding_registry(self) -> BindingRegistry:
        return self._binding_registry

    @classmethod
    def add_condition(cls, condition: Condition):
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
        # pylint: disable=import-outside-toplevel
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
                        item_bindings=[
                            RegisteredBinding(
                                registered_item_binding.raw_binding,
                                (module_instance,) + binding.source_path,
                            )
                            for registered_item_binding in binding.item_bindings
                        ],
                    )
                else:
                    binding = RegisteredBinding(
                        binding.raw_binding,
                        (module_instance,) + binding.source_path,
                    )
            self._binding_registry.register(binding, add_self_binding=False)

    # pylint: disable=too-many-arguments
    def bind(
        self,
        target_type: Union[Type[InjectedT], "TypeVar"],
        *,
        to_class: Type[InjectedT] = EMPTY,
        to_instance: InjectedT = EMPTY,
        to_provider: Union[Provider, Type[Provider], Callable[..., InjectedT]] = EMPTY,
        scope: Type[Scope] = SingletonScope,
        named: Optional[str] = None,
    ) -> RegisteredBinding:
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
            if all(condition.is_valid() for condition in self.conditions):
                self.configure()

    def multi_bind(
        self,
        item_target_type: Union[Type[InjectedT], "TypeVar"],
        item_bindings: List[ItemBinding[InjectedT]],
        *,
        scope: Type[Scope] = SingletonScope,
        named: Optional[str] = None,
        override_bindings: bool = True,
    ) -> RegisteredBinding:

        return self._register_multi_binding(
            MultiBinding(item_target_type, item_bindings, scope=scope, named=named, override_bindings=override_bindings)
        )

    @staticmethod
    def bind_item(
        *,
        to_class: Type[InjectedT] = EMPTY,
        to_instance: InjectedT = EMPTY,
        to_provider: Union[Provider, Type[Provider], Callable[..., InjectedT]] = EMPTY,
    ) -> ItemBinding[InjectedT]:
        return ItemBinding(bound_class=to_class, bound_instance=to_instance, bound_provider=to_provider)

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
        target_type: Union[Type[InjectedT], "TypeVar"],
        bound_class: Type[InjectedT],
        bound_instance: InjectedT,
        bound_provider: Union[Provider, Type[Provider], Callable[..., InjectedT]],
        scope: Type[Scope],
        named: Optional[str],
    ) -> Binding:
        if bound_instance is not EMPTY:
            return InstanceBinding(target_type, bound_instance, named=named)
        if bound_provider is not EMPTY:
            return ProviderBinding(target_type, bound_provider, scope=scope, named=named)
        if bound_class is not EMPTY and bound_class != target_type:
            return ClassBinding(target_type, bound_class, scope=scope, named=named)
        return SelfBinding(target_type, scope=scope, named=named)

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
            if item_binding.bound_class is not EMPTY:
                item_binding = SelfBinding(
                    item_binding.bound_class,
                    scope=binding.scope,
                    named=binding.named,
                )
            elif item_binding.bound_instance is not EMPTY:
                item_binding = InstanceBinding(
                    binding.item_target_type,
                    item_binding.bound_instance,
                    named=binding.named,
                )
            elif item_binding.bound_provider is not EMPTY:
                item_binding = ProviderBinding(
                    binding.item_target_type,
                    item_binding.bound_provider,
                    scope=binding.scope,
                    named=binding.named,
                )
            else:
                raise BindingError(f"ItemBinding in {binding!r} has no instance, class or provider, one should be set")

            # pylint: disable=no-member
            registered_binding.item_bindings.append(RegisteredBinding(item_binding))
        self._binding_registry.register(registered_binding)
        return registered_binding
