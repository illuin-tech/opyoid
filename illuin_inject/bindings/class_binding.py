import logging
from typing import Type

import attr

from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT
from .binding import Binding


@attr.s(auto_attribs=True)
class ClassBinding(Binding[InjectedT]):
    logger = logging.getLogger(__name__)

    bound_type: Type[InjectedT] = attr.Factory(lambda self: self.target_type, takes_self=True)
    scope: Type[Scope] = SingletonScope
