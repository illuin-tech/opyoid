import logging
from typing import Optional, Type

import attr

from illuin_inject.typings import InjectedT
from .binding import Binding


@attr.s(auto_attribs=True, init=False, kw_only=True)
class InstanceBinding(Binding[InjectedT]):
    logger = logging.getLogger(__name__)

    bound_instance: InjectedT

    def __init__(self,
                 target_type: Type[InjectedT],
                 bound_instance: InjectedT,
                 annotation: Optional[str] = None):
        self.target_type = target_type
        self.bound_instance = bound_instance
        self.annotation = annotation
