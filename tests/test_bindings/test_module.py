import unittest

from opyoid import Module


class TestModule(unittest.TestCase):
    def setUp(self) -> None:
        self.module = Module()

    def test_configure_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.module.configure()
