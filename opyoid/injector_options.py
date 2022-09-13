import attr


@attr.s(auto_attribs=True, kw_only=True)
class InjectorOptions:
    """
    :param auto_bindings: if True, missing bindings will be generated when needed instead of raising an Exception
    :param use_env_vars: if True, environment variables will be loaded to override bindings for built_in types
    """

    auto_bindings: bool = False
    use_env_vars: bool = True
