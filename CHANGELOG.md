# Changelog
## Unreleased
### Features
- Added `Tuple` and `Set` injection


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
