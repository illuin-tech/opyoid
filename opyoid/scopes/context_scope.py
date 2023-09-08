from types import TracebackType
from typing import Any, List, Optional, Type

from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .context_scoped_provider import ContextScopedProvider
from .scope import Scope


class ContextScope(Scope):
    """Always provides the same instance in the same context, a new instance in each context."""

    def __init__(self) -> None:
        self._scoped_providers: List[ContextScopedProvider[Any]] = []

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        scoped_provider = ContextScopedProvider(inner_provider)
        self._scoped_providers.append(scoped_provider)
        return scoped_provider

    def __enter__(self) -> None:
        for provider in self._scoped_providers:
            provider.enter()

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        for provider in self._scoped_providers:
            provider.exit()
