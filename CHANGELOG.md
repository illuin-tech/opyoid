# Changelog
## Unreleased
### Breaking changes
- Removed `scopes_by_type` argument from the `Injector` constructor, it is not needed anymore to inject custom scopes
- Custom scopes must now be injected. By default, `SingletonScope`, `ThreadScope`, `ImmediateScope` and `PerLookupScope`
 are bound, but they can be overridden. `SingletonScope` can only be bound in an instance binding.


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
