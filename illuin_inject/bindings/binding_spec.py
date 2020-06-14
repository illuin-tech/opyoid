from typing import List, Optional, Type, Union

from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import EMPTY, InjectedT
from .binding_registry import BindingRegistry
from .class_binding import ClassBinding
from .factory_binding import FactoryBinding
from .instance_binding import InstanceBinding
from .multi_binding import ItemBinding, MultiBinding


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
        These can be scoped as singletons (by default), per lookup (a new instance is injected every time),
        immediately (same as singleton, but will be instantiated as soon as the injector is created), or in a thread
        scope (a new instance will be created for each thread)
            self.bind(MyAbstractClass, MyImplementationClass, scope=SingletonScope)
            self.bind(MyClass, scope=PerLookupScope)
            self.bind(MyClass, scope=ImmediateScope)
            self.bind(MyClass, scope=ThreadScope)
        - Binding a class to an instance of it
            self.bind(MyClass, to_instance=MyInstance)
        - Binding a class to a Factory providing it
            self.bind(MyClass, to_factory=MyFactory)
            self.bind(MyClass, to_factory=MyFactory())
            self.bind(MyClass, to_factory=MyFactory, scope=PerLookupScope)

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
        if to_class is EMPTY and to_instance is EMPTY and to_factory is EMPTY:
            to_class = target_type
        try:
            self._register_binding(target_type, to_class, to_instance, to_factory, scope, annotation)
        except BindingError as error:
            raise BindingError(f"Error in {self!r} when binding to {target_type!r}: {error}") from None

    def multi_bind(self,
                   item_target_type: Type[InjectedT],
                   item_bindings: List[ItemBinding[InjectedT]],
                   scope: Type[Scope] = SingletonScope,
                   annotation: Optional[str] = None,
                   override_bindings: bool = True) -> None:
        self._binding_registry.register(
            MultiBinding(item_target_type, item_bindings, scope, annotation, override_bindings)
        )

    @staticmethod
    def bind_item(to_class: Type[InjectedT] = EMPTY,
                  to_instance: InjectedT = EMPTY,
                  to_factory: Union[Factory, Type[Factory]] = EMPTY) -> ItemBinding[InjectedT]:
        return ItemBinding(to_class, to_instance, to_factory)

    def _register_binding(self,
                          target_type: Type[InjectedT],
                          bound_type: Type[InjectedT],
                          bound_instance: InjectedT,
                          bound_factory: Union[Factory, Type[Factory]],
                          scope: Type[Scope],
                          annotation: Optional[str]) -> None:
        if bound_instance is not EMPTY:
            if scope is not SingletonScope:
                raise BindingError("Cannot set a scope to an instance")
            binding = InstanceBinding(target_type, bound_instance, annotation)
        elif bound_factory is not EMPTY:
            binding = FactoryBinding(target_type, bound_factory, scope, annotation)
        else:
            binding = ClassBinding(target_type, bound_type, scope, annotation)
        self._binding_registry.register(binding)

    def __repr__(self) -> str:
        return ".".join([self.__class__.__module__, self.__class__.__qualname__])
