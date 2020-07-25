Private bindings
================

### The problem
Sometimes you need to inject several instances of the same class with different dependencies.

Using annotations only cannot solve this, this problem is also called the robot legs problem.


### The solution

Using a PrivateBindingSpec allows you to bind multiple classes to the same type and annotation.

By default bindings are only available to other classes bound in the same private binding spec.
You can expose some of them with `self.expose(self.bind(...))`, they become available in the binding spec installing
them (or globally if you use them in the injector constructor).

```python
from illuin_inject import Injector, PrivateBindingSpec


class MyAbstractClass:
    pass


class MyImplementation1(MyAbstractClass):
    pass


class MyImplementation2(MyAbstractClass):
    pass


class MyParentClass:
    def __init__(self, my_param: MyAbstractClass):
        self.my_param = my_param


class MyPrivateBindingSpec1(PrivateBindingSpec):
    def configure(self):
        self.bind(MyAbstractClass, MyImplementation1)
        self.expose(
            self.bind(MyParentClass, annotation="impl1")
        )

class MyPrivateBindingSpec2(PrivateBindingSpec):
    def configure(self):
        self.bind(MyAbstractClass, MyImplementation2)
        self.expose(
            self.bind(MyParentClass, annotation="impl2")
        )


injector = Injector([MyPrivateBindingSpec1(), MyPrivateBindingSpec2()])
parent_1 = injector.inject(MyParentClass, "impl1")
parent_2 = injector.inject(MyParentClass, "impl2")
assert isinstance(parent_1, MyParentClass)
assert isinstance(parent_2, MyParentClass)
assert isinstance(parent_1.my_param, MyImplementation1)
assert isinstance(parent_2.my_param, MyImplementation2)
```
