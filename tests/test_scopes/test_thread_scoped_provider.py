import unittest
from queue import Queue
from threading import Thread
from unittest.mock import create_autospec

from opyoid.bindings import FromCallableProvider
from opyoid.injection_context import InjectionContext
from opyoid.scopes.thread_scoped_provider import ThreadScopedProvider


class MyType:
    pass


class TestThreadScopedProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.context = create_autospec(InjectionContext, spec_set=True)
        self.class_provider = FromCallableProvider(MyType, [], None, {}, self.context)
        self.provider = ThreadScopedProvider(self.class_provider)

    def test_get_returns_instance(self):
        instance = self.provider.get()

        self.assertIsInstance(instance, MyType)

    def test_multiple_get_return_same_instance(self):
        instance_1 = self.provider.get()
        instance_2 = self.provider.get()

        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
        self.assertIs(instance_1, instance_2)

    def test_different_threads_return_different_instances(self):
        instance_1 = self.provider.get()
        queue = Queue()

        def put_in_queue():
            queue.put(self.provider.get())

        thread = Thread(target=put_in_queue)
        thread.start()
        thread.join(1)
        instance_2 = queue.get()
        instance_3 = self.provider.get()

        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
        self.assertIsInstance(instance_3, MyType)
        self.assertIs(instance_1, instance_3)
        self.assertIsNot(instance_1, instance_2)
        self.assertIsNot(instance_2, instance_3)

    def test_cache_is_not_shared_between_providers(self):
        provider_2 = ThreadScopedProvider(self.class_provider)
        instance_1 = self.provider.get()
        instance_2 = provider_2.get()

        self.assertIsNot(instance_1, instance_2)
