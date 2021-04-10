Private bindings
================

### The problem
Sometimes you need to inject several instances of the same class with different dependencies.

Using named arguments only cannot solve this, this problem is also called the robot legs problem.


### The solution

Using a PrivateModule allows you to bind multiple classes to the same type and name.

By default bindings are only available to other classes bound in the same private module.
You can expose some of them with `self.expose(self.bind(...))`, they become available in the module installing
them (or globally if you use them in the injector constructor).

```python
from opyoid import Injector, PrivateModule


class MyAbstractClass:
    pass


class MyImplementation1(MyAbstractClass):
    pass


class MyImplementation2(MyAbstractClass):
    pass


class MyParentClass:
    def __init__(self, my_param: MyAbstractClass):
        self.my_param = my_param


class MyPrivateModule1(PrivateModule):
    def configure(self):
        self.bind(MyAbstractClass, to_class=MyImplementation1)
        self.expose(
            self.bind(MyParentClass, named="impl1")
        )

class MyPrivateModule2(PrivateModule):
    def configure(self):
        self.bind(MyAbstractClass, to_class=MyImplementation2)
        self.expose(
            self.bind(MyParentClass, named="impl2")
        )


injector = Injector([MyPrivateModule1(), MyPrivateModule2()])
parent_1 = injector.inject(MyParentClass, named="impl1")
parent_2 = injector.inject(MyParentClass, named="impl2")
assert isinstance(parent_1, MyParentClass)
assert isinstance(parent_2, MyParentClass)
assert isinstance(parent_1.my_param, MyImplementation1)
assert isinstance(parent_2.my_param, MyImplementation2)
```

### Using MultiBindings

You can also expose MultiBindings the same way:

```python
from typing import List

from opyoid import Injector, PrivateModule, SelfBinding


class MyAbstractClass:
    pass


class MyImplementation1(MyAbstractClass):
    pass


class MyImplementation2(MyAbstractClass):
    pass


class MyParentClass:
    def __init__(self, my_param: List[MyAbstractClass]):
        self.my_param = my_param


class MyPrivateModule1(PrivateModule):
    def configure(self):
        self.expose(
            self.multi_bind(MyAbstractClass, [
                self.bind_item(to_class=MyImplementation1)
            ])
        )

class MyPrivateModule2(PrivateModule):
    def configure(self):
        self.expose(
            self.multi_bind(
                MyAbstractClass,
                [
                    self.bind_item(to_class=MyImplementation2)
                ],
                override_bindings=False  # Don't forget this or it will override the other item binding
            )
        )


injector = Injector([MyPrivateModule1(), MyPrivateModule2()], [SelfBinding(MyParentClass)])
parent = injector.inject(MyParentClass)
assert len(parent.my_param) == 2
assert isinstance(parent.my_param[0], MyImplementation1)
assert isinstance(parent.my_param[1], MyImplementation2)

```
Each item dependencies will get resolved from their respective PrivateModule, this is useful is you want independent
items.
