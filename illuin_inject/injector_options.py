import attr


@attr.s(auto_attribs=True)
class InjectorOptions:
    auto_bindings: bool = False
