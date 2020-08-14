import unittest
from queue import Queue
from threading import Thread

from illuin_inject.bindings import FromClassProvider
from illuin_inject.scopes.singleton_scoped_provider import SingletonScopedProvider


class MyType:
    pass


class TestSingletonScopedProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.class_provider = FromClassProvider(MyType, [], None, {})
        self.provider = SingletonScopedProvider(self.class_provider)

    def test_get_returns_instance(self):
        instance = self.provider.get()

        self.assertIsInstance(instance, MyType)

    def test_multiple_get_return_same_instance(self):
        instance_1 = self.provider.get()
        instance_2 = self.provider.get()

        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
        self.assertIs(instance_1, instance_2)

    def test_different_threads_return_same_instance(self):
        instance_1 = self.provider.get()
        queue = Queue()

        def put_in_queue():
            queue.put(self.provider.get())

        thread = Thread(target=put_in_queue)
        thread.start()
        thread.join(1)
        instance_2 = queue.get()

        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
        self.assertIs(instance_1, instance_2)

    def test_cache_is_not_shared_between_providers(self):
        provider_2 = SingletonScopedProvider(self.class_provider)
        instance_1 = self.provider.get()
        instance_2 = provider_2.get()

        self.assertIsNot(instance_1, instance_2)
