from typing import Optional, Type, Union

from .binding_registry import BindingRegistry
from .bindings import ClassBinding, FactoryBinding, InstanceBinding
from .exceptions import BindingError
from .factory import Factory
from .scopes import Scope, SingletonScope
from .typings import InjectedT

EMPTY = object()


class BindingSpec:
    def __init__(self) -> None:
        self._binding_registry = BindingRegistry()

    @property
    def binding_registry(self) -> BindingRegistry:
        return self._binding_registry

    def configure(self) -> None:
        """Contains all bindings, called at injector initialization.

        The self.bind method can be called with different arguments:
        - Binding a class to itself
            self.bind(MyClass)
        - Binding a class to its subclass
            self.bind(MyClass, MyImplementation)
        These can be scoped as singletons (by default), per lookup (a new instance is injected every time) or
        immediately (same as singleton, but will be instantiated as soon as the injector is created)
            self.bind(MyAbstractClass, MyImplementationClass, scope=SingletonScope)
            self.bind(MyClass, scope=PerLookupScope)
            self.bind(MyClass, scope=ImmediateScope)
        - Binding a class to an instance of it
            self.bind(MyClass, to_instance=MyInstance)
        - Binding a class to a Factory providing it
            self.bind(MyClass, to_factory=MyFactory)
            self.bind(MyClass, to_factory=MyFactory())
            self.bind(MyClass, to_factory=MyFactory, scope=)

        You can also include another BindingSpec with install:
            self.install(OtherBindingSpecInstance)
        """
        raise NotImplementedError

    def install(self, binding_spec: "BindingSpec") -> None:
        binding_spec.configure()
        self._binding_registry.update(binding_spec.binding_registry)

    # pylint: disable=too-many-arguments
    def bind(self,
             target_type: Type[InjectedT],
             to_class: Type[InjectedT] = EMPTY,
             to_instance: InjectedT = EMPTY,
             to_factory: Union[Factory, Type[Factory]] = EMPTY,
             scope: Type[Scope] = SingletonScope,
             annotation: Optional[str] = None) -> None:
        self._check_args(
            target_type,
            to_class,
            to_instance,
            to_factory,
            scope,
        )
        if to_class is EMPTY and to_instance is EMPTY and to_factory is EMPTY:
            to_class = target_type
        self._register_binding(target_type, to_class, to_instance, to_factory, scope, annotation)

    def _register_binding(self,
                          target_type: Type[InjectedT],
                          bound_type: Type[InjectedT],
                          bound_instance: InjectedT,
                          bound_factory: Union[Factory, Type[Factory]],
                          scope: Type[Scope],
                          annotation: Optional[str]) -> None:
        if bound_type is not EMPTY:
            binding = ClassBinding(target_type, bound_type, scope, annotation)
        elif bound_instance is not EMPTY:
            binding = InstanceBinding(target_type, bound_instance, annotation)
        else:
            binding = FactoryBinding(target_type, bound_factory, scope, annotation)
        self._binding_registry.register(binding)

    @staticmethod
    def _check_args(target_type: Type[InjectedT],
                    to_class: Type[InjectedT],
                    to_instance: InjectedT,
                    to_factory: Union[Factory, Type[Factory]],
                    scope: Type[Scope]):
        non_empty_params = [
            param
            for param in (to_class, to_instance, to_factory)
            if param is not EMPTY
        ]
        if len(non_empty_params) > 1:
            raise BindingError(
                f"Cannot bind a class, an instance or a factory at the same time to {target_type.__name__}")
        if to_instance is not EMPTY and scope is not SingletonScope:
            raise BindingError(f"Can only bind instance {to_instance!r} to a singleton scope")
        if to_factory is not EMPTY \
                and not isinstance(to_factory, Factory) \
                and not (isinstance(to_factory, type) and issubclass(to_factory, Factory)):
            raise BindingError(f"Factory must be either an instance or a subclass of Factory, got {to_factory!r}")
