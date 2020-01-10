import unittest
from queue import Queue
from threading import Thread

from illuin_inject.scopes.thread_scope import ThreadScope


class MyClass:
    pass


def provider():
    return MyClass()


class TestThreadScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = ThreadScope()

    def test_get_returns_instance(self):
        instance = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance, MyClass)

    def test_multiple_get_return_same_instance(self):
        instance_1 = self.scope.get(MyClass, provider)
        instance_2 = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_2, MyClass)
        self.assertIs(instance_1, instance_2)

    def test_different_threads_return_different_instances(self):
        instance_1 = self.scope.get(MyClass, provider)
        queue = Queue()

        def put_in_queue():
            queue.put(self.scope.get(MyClass, provider))

        thread = Thread(target=put_in_queue)
        thread.start()
        thread.join(1)
        instance_2 = queue.get()
        instance_3 = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_2, MyClass)
        self.assertIsInstance(instance_3, MyClass)
        self.assertIs(instance_1, instance_3)
        self.assertIsNot(instance_1, instance_2)
        self.assertIsNot(instance_2, instance_3)
