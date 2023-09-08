# Changelog

Opyoid follows [semver guidelines](https://semver.org) for versioning.

## Unreleased
## 2.0.0
### Breaking changes
- Remove support for Python < 3.8
- MultiBindings now have the parameter `override_bindings` set to `False` by default (was `True`)

## 1.7.0
### Features
- Add official support for Python 3.11
- Opyoid is now PEP561 compliant, and as such compatible with mypy
- Added a Context Scope that can be used to control more precisely the scope of created objects:
```python
from opyoid import ContextScope, Injector, SelfBinding

class MyClass:
  pass


injector = Injector(bindings=[SelfBinding(MyClass, scope=ContextScope)])
scope = injector.inject(ContextScope)

with scope:
    instance_1 = injector.inject(MyClass)
    instance_2 = injector.inject(MyClass)

with scope:
    instance_3 = injector.inject(MyClass)

assert instance_1 is instance_2
assert instance_1 is not instance_3
```

## 1.6.0
### Features
- Built-in types such as strings, ints, floats and booleans can be loaded from enviroment variables
  - The environment variable name should be `<UPPER_CLASS_NAME_UPPER_PARAMTER_NAME>`
  - Use InjectorOptions.use_env_vars to enable/disable the feature (activated by default)
  - Check the docs for more details

## 1.5.1
### Fixes
- Fixed unwanted bindings being automatically created when using InstanceBindings with builtin types

## 1.5.0
### Features
- Added `named` and `scope` parameters to item bindings, by default they keep the parent MultiBinding name and scope
(as they did before)

## 1.4.0
### Features
- Module classes can now be installed (instances can still be installed), the contained bindings will be created only
once if the module class installed multiple times
- Provider bindings can now bind any typed function as a provider, this is now the preferred way to create providers but
provider classes are still supported

### Fixed
- Fixed missing bindings in log when adding item bindings to a previously existing multi binding

## 1.3.0
### Features
- Instances created from a class in a MultiBinding with a Singleton scope can now be reused
  - If you have a class A that requires List[B], a multibinding on B that binds subclasses B1 and B2,
    and another class C that requires B1, the same instance of B1 will be shared between A and the list in C


## 1.2.0
### Features
- Added `conditional_on_env_var` decorator that can be put on modules to easily enable / disable them through
environment variables


## 1.1.0
### Features
- Added official support for Python 3.10
- Added support for Union[...] type, which injects the first item type for which bindings exist
- Added support for List[Union[...]] type, which injects a list combining all the items types in the union


## 1.0.1
### Fixes
- Using auto bindings does not ignore existing bindings anymore (bug introduced in `0.10.0`)
- The error message in cyclic dependency errors is now displaying the dependencies in a more logical order
  (from the parent class to the dependencies)


## 1.0.0
### Breaking changes
- Renamed `bound_type` argument in `ClassBinding` and `ItemBinding` constructors into `bound_class`
- Several method signatures now have keyword-only arguments:
  - `named` in `Injector.inject`
  - `to_class`, `to_instance`, `to_provider`, `scope` and `named` in `AbstractModule.bind`
  - `scope`, `named` and `override_bindings` in `AbstractModule.multi_bind`
  - `to_class`, `to_instance` and `to_provider` in `AbstractModule.bind_item`
  - `scope` and `named` in `ClassBinding.__init__`
  - `bound_class`, `bound_instance`, `bound_provider` in `ItemBinding.__init__`
  - `named` in `InstanceBinding.__init__`
  - `scope`, `named` and `override_bindings` in `MultiBinding.__init__`
  - `scope` and `named` in `ProviderBinding.__init__`
  - `scope` and `named` in `SelfBinding.__init__`
  - `auto_bindings` in `InjectorOptions.__init__`

### Features
- Opyoid is now considered stable


## 0.10.3
### Fixes
- Improved error message when missing a named binding, the underlying type and name is used


## 0.10.2
### Fixes
- Improved repr of named types, the original type is now used


## 0.10.1
### Fixes
- Improved repr of generic types, the full name is now used


## 0.10.0
### Breaking changes
- Replaced `@annotated_arg` with `@named_arg`
- Renamed the `annotation` parameter to `named` in:
    - all Binding subclasses
    - the `AbstractModule.bind` method
    - the `Injector.inject` method
- Changed the way annotated/named arguments work:
    - When injecting a parameter in a constructor, opyoid will first try to find a binding with the same type and the
    same name as the argument. If none is found, it will then try to find a binding with the same type and no name (this
     part did not change).
    - If the `@named_arg` decorator is used, opyoid will only try to find a binding with this name, if none is found, no
    unnamed binding will be used (this did not change).

### Features
- Cyclic dependencies now raise a `CyclicDependencyError` instead of a `RecursionError`
- Cleaner and more verbose logs

### Fixes
- Removed duplicate logs about registering bindings


## 0.9.0
### Breaking changes
- ClassBindings cannot be used to bind a class to itself anymore, use a SelfBinding instead

### Features
- When binding to a target an instance of a subclass of the target type, another InstanceBinding is created with the
same instance and its type as a target
- When binding to a target an instance of a provider, another InstanceBinding is created with the same provider and its
type as a target

### Fixes
- Fixed Bindings with a target being overriden by `ClassBindings` with the same target as a `bound_type`


## 0.8.0
### Features
- Support for PEP585 style type hints (list[str], set[str], ...)


## 0.7.0
### Features
- MultiBindings can now be exposed by PrivateModules

### Fixes
- Binding Provider classes in ItemBindings now works as expected


## 0.6.2
### Fixes
- Non hashable instance bindings can be exposed in private modules


## 0.6.1
### Fixes
- Fixed a bug preventing injection when using strings as type hints


## 0.6.0
### Breaking changes
- Using `auto_bindings=True` will only create a new instance for a parameter if there is no default value.


## 0.5.0
### Breaking changes
- Renamed library name to `opyoid`
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
