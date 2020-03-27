from .singleton_scope import SingletonScope


class ImmediateScope(SingletonScope):
    """Always provides the same instance, objects are instantiated immediately."""
