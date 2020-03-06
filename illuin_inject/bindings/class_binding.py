import logging
from typing import Optional, Type

import attr

from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT
from .binding import Binding


@attr.s(auto_attribs=True, init=False, kw_only=True)
class ClassBinding(Binding[InjectedT]):
    logger = logging.getLogger(__name__)

    bound_type: Type[InjectedT]
    scope: Type[Scope]

    def __init__(self,
                 target_type: Type[InjectedT],
                 bound_type: Type[InjectedT] = None,
                 scope: Type[Scope] = SingletonScope,
                 annotation: Optional[str] = None):
        self.target_type = target_type
        self.bound_type = bound_type or target_type
        self.scope = scope
        self.annotation = annotation
