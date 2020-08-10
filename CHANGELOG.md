# Changelog
## Unreleased
### Breaking changes
- Removed `scopes_by_type` argument from the `Injector` constructor, it is not needed anymore to inject custom scopes
- Custom scopes must now be bound to `Scope`. By default, `SingletonScope`, `ThreadScope`, `ImmediateScope` and
`PerLookupScope` are bound, but they can be overridden. `SingletonScope` can only be bound in an instance binding.
- `Scope.get_scoped_provider` is now an instance method, it used to be a class method
- Renamed `BindingSpec` to `Module`
- Renamed `binding_specs` argument to `modules` in Injector constructor
- Lists, sets and tuples must now be bound using `MultiBinding`. You can create one from your modules:
```python
class MyModule(Module):
    def configure(self):
        self.multi_bind(MyClass, [
            self.bind_item(MySubClass1),
            self.bind_item(MySubClass2),
        ])
```
More details are available in the documentation.
- Singletons are now shared between bindings. This means that if you bind the same implementation to two different
classes, the same instance will be injected for each class.
- Renamed `Factory` to `Provider`
- Renamed `FactoryBinding` to `ProviderBinding`
- Renamed `to_factory` argument to `to_provider` in the `Module.bind` method

### Features
- Added `MultiBinding` and `ItemBinding`
- Added `PrivateBindingSpec`
- Added `options: InjectorOptions` argument to the `Injector` constructor, it has an `auto_bindings: bool = False`
argument that can be used to implicitly bind all classes to themselves in a SingletonScope.
- Added `Provider` injection, you can now inject `Provider[MyClass]` and it will return a provider that can be used for
delayed instantiation. If a `ProviderBinding` exists with the right type it will be used instead of creating a new
provider. 

### Fixes
- You can now bind any binding to a Provider class, by default a ClassBinding with the provider class will be created


## 0.4.0
### Breaking changes
- Singleton, Immediate and Thread scopes are now guaranteeing that only one instance of a class can be created for
each ClassBinding or FactoryBindings, instead of one instance per bound_type.
You can now have multiple instance of the same class if you create multiple bindings instantiating it.

### Features
- Added `FactoryBinding`
- Added `to_factory: Optional[Union[Type[Factory], Factory]]` argument in `BindingsSpec.bind` method

### Fixed
- Adding multiple bindings of the same class with different annotations in the SingletonScope will create different
instances, one per binding.


## 0.3.1
### Fixes
- Fixed an exception being raised when injecting a union of generic types


## 0.3.0
### Features
- Added `Tuple` and `Set` injection
- Added `ImmediateScope`


## 0.2.0
### Features
- Added python>=3.7 compatibility
- Added `@annotated_arg(arg_name, annotation)` decorator
- Added `annotation: Optional[str]` parameter in `InstanceBinding` and `ClassBinding` constructors
- Added `annotation: Optional[str]` parameter in `Injector.inject(target_type: Type[InjectedT], annotation: Optional[str] = None)`
- Added `annotation: Optional[str]` parameter in `BindingsSpec.bind` method


## 0.1.0
### Features
- Added `Injector`
- Added `BindingSpec`
- Added `ClassBinding` and `InstanceBinding`
- Added `SingletonScope`, `PerLookupScope` and `ThreadScope`
