from typing import Type

from .binding_registry import BindingRegistry
from .bindings import ClassBinding, InstanceBinding
from .exceptions import BindingError
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
        - Binding a subclass to a class
            self.bind(MyClass, MyImplementation)
        These can be scoped as singletons (by default) or per lookup (a new instance is injected every time)
            self.bind(MyClass, scope=IMMEDIATE_SCOPE)
            self.bind(MyAbstractClass, MyImplementationClass, scope=SINGLETON_SCOPE)
        - Binding an instance to its class
            self.bind(MyClass, to_instance=MyInstance)

        You can also include another BindingSpec with install:
            self.install(OtherBindingSpecInstance)
        """
        raise NotImplementedError

    def install(self, binding_spec: "BindingSpec") -> None:
        binding_spec.configure()
        self._binding_registry.update(binding_spec.binding_registry)

    def bind(self,
             target_type: Type[InjectedT],
             to_class: Type[InjectedT] = EMPTY,
             to_instance: InjectedT = EMPTY,
             scope: Type[Scope] = SingletonScope) -> None:
        if to_class is not EMPTY and to_instance is not EMPTY:
            raise BindingError(f"Cannot bind a class and an instance at the same time to {target_type.__name__}")
        if to_instance is not EMPTY and scope is not SingletonScope:
            raise BindingError(f"Cannot only bind instance {to_instance!r} to a singleton scope")
        if to_class is EMPTY and to_instance is EMPTY:
            to_class = target_type
        self._register_binding(target_type, to_class, scope, to_instance)

    def _register_binding(self,
                          target_type: Type[InjectedT],
                          bound_type: Type[InjectedT],
                          scope: Type[Scope],
                          bound_instance: InjectedT) -> None:
        if bound_type is not EMPTY:
            binding = ClassBinding(target_type, bound_type, scope)
        else:
            binding = InstanceBinding(target_type, bound_instance)
        self._binding_registry.register(binding)
