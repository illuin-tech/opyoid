import logging
from typing import Optional, Type, Union

import attr

from illuin_inject.factory import Factory
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT
from .binding import Binding


@attr.s(auto_attribs=True, init=False, kw_only=True)
class FactoryBinding(Binding[InjectedT]):
    logger = logging.getLogger(__name__)

    bound_factory: Union[Type[Factory[InjectedT]], Factory[InjectedT]]
    scope: Type[Scope]

    def __init__(self,
                 target_type: Type[InjectedT],
                 bound_factory: Union[Type[Factory[InjectedT]], Factory[InjectedT]],
                 scope: Type[Scope] = SingletonScope,
                 annotation: Optional[str] = None):
        self.target_type = target_type
        self.bound_factory = bound_factory
        self.scope = scope
        self.annotation = annotation
