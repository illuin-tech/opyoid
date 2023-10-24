from typing import Any, Callable, Dict, List, Optional

from opyoid.bindings.self_binding.parameters_provider import ParametersProvider
from opyoid.constants import OPYOID_POST_INIT
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT


class FromCallableProvider(Provider[InjectedT]):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        injected_callable: Callable[..., InjectedT],
        positional_providers: List[Provider[Any]],
        args_provider: Optional[Provider[List[Any]]],
        keyword_providers: Dict[str, Provider[Any]],
        injection_context: InjectionContext[InjectedT],
    ) -> None:
        self._injected_callable = injected_callable
        self._positional_providers = positional_providers
        self._args_provider = args_provider
        self._keyword_providers = keyword_providers
        self._injection_context = injection_context
        self._parameters_provider = ParametersProvider()

    def get(self) -> InjectedT:
        args = [positional_provider.get() for positional_provider in self._positional_providers]
        if self._args_provider:
            args += self._args_provider.get()
        kwargs = {arg_name: keyword_provider.get() for arg_name, keyword_provider in self._keyword_providers.items()}
        result = self._injected_callable(
            *args,
            **kwargs,
        )
        if hasattr(self._injected_callable, OPYOID_POST_INIT):
            self._injection_context.injection_state.add_post_init_callback(lambda: self._run_post_init(result))
        return result

    def _run_post_init(self, instance: InjectedT) -> None:
        (
            post_init_positional_providers,
            post_init_args_provider,
            post_init_keyword_providers,
        ) = self._parameters_provider.get_parameters_provider(
            getattr(instance, OPYOID_POST_INIT),
            self._injection_context,
        )

        post_init_args = [positional_provider.get() for positional_provider in post_init_positional_providers]
        if post_init_args_provider:
            post_init_args += post_init_args_provider.get()
        post_init_kwargs = {
            arg_name: keyword_provider.get() for arg_name, keyword_provider in post_init_keyword_providers.items()
        }
        getattr(instance, OPYOID_POST_INIT)(*post_init_args, **post_init_kwargs)
