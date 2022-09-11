# Environment Variables

You can use environment variables to easily override bindings in your application.

### Supported types

Supported types are `str`, `int`, `float`, and `bool`.

Environment variables are only used when loading ClassBindings, ProviderBindings or SelfBindings, not InstanceBindings

If the corresponding environment variable exists, it will override the existing default value and bindings for the
parameter.

### Environment variable name

The environment variable should be named `UPPER_CLASS_NAME_UPPER_PARAMETER_NAME`
In this example, the environment variable to set is `MY_CLASS_MY_PARAMETER`:
```python
@dataclass
class MyClass:
    my_parameter: int
```

### Value conversion

For types other than str, an automatic conversion is made:
- ints and floats are converted using int() and float()
- for booleans, authorized values are:
  - "0", "false" and "False", will be converted to `False`
  - "1", "true" and "True", will be converted to `True`
