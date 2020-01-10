import unittest

from illuin_inject.scopes import Scope


class TestScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = Scope()

    def test_get_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.scope.get(str, lambda: "hello")

    def test_repr(self):
        self.assertIn("Scope", repr(self.scope))
