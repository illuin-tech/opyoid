import unittest
from queue import Queue
from threading import Thread

from illuin_inject import ImmediateScope


class MyClass:
    pass


def provider():
    return MyClass()


class TestImmediateScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = ImmediateScope()

    def test_get_returns_instance(self):
        instance = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance, MyClass)

    def test_multiple_get_return_same_instance(self):
        instance_1 = self.scope.get(MyClass, provider)
        instance_2 = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_2, MyClass)
        self.assertIs(instance_1, instance_2)

    def test_different_threads_return_same_instance(self):
        instance_1 = self.scope.get(MyClass, provider)
        queue = Queue()

        def put_in_queue():
            queue.put(self.scope.get(MyClass, provider))

        thread = Thread(target=put_in_queue)
        thread.start()
        thread.join(1)
        instance_2 = queue.get()

        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_2, MyClass)
        self.assertIs(instance_1, instance_2)

    def test_cache_is_not_shared_between_scopes(self):
        scope_2 = ImmediateScope()
        instance_1 = self.scope.get(MyClass, provider)
        instance_2 = scope_2.get(MyClass, provider)

        self.assertIsNot(instance_1, instance_2)
