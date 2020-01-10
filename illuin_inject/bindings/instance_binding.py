import logging

import attr

from illuin_inject.typings import InjectedT
from .binding import Binding


@attr.s(auto_attribs=True)
class InstanceBinding(Binding[InjectedT]):
    logger = logging.getLogger(__name__)

    bound_instance: InjectedT
