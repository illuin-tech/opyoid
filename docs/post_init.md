# Post init

You can sometimes end up having a dependency loop: A requires B and B requires A.
Most of the time this is due to a code structuring issue and needs refactoring, but it can also be the only way to solve
a problem.

The `__opyoid_post_init__` method helps to break this dependency loop by adding additional attributes to the instances 
after they are instantiated.

```python
from opyoid import Injector, SelfBinding
from typing import Optional

class ClassA:
    def __init__(self, my_arg: "ClassB"):
        self.my_arg = my_arg

class ClassB:
    def __init__(
        self,
    ) -> None:
        self.my_arg: Optional[ClassA] = None

    def __opyoid_post_init__(self, my_arg: ClassA) -> None:
        self.my_arg = my_arg

injector = Injector(bindings=[SelfBinding(ClassA), SelfBinding(ClassB)])

instance_a = injector.inject(ClassA)
instance_b = injector.inject(ClassB)

assert isinstance(instance_a, ClassA)
assert isinstance(instance_b, ClassB)
assert instance_a.my_arg is instance_b
assert instance_b.my_arg is instance_a
```
