from .abstract_module import AbstractModule


class Module(AbstractModule):
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
        - Binding a class to a Provider providing it
            self.bind(MyClass, to_provider=MyProvider)
            self.bind(MyClass, to_provider=MyProvider())
            self.bind(MyClass, to_provider=MyProvider, scope=PerLookupScope)

        You can also include another Module with install:
            self.install(OtherModuleInstance)
        """
        raise NotImplementedError
