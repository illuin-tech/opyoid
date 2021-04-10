import attr


@attr.s(auto_attribs=True, kw_only=True)
class InjectorOptions:
    auto_bindings: bool = False
