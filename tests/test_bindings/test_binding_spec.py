import unittest

from illuin_inject import BindingSpec


class TestBindingSpec(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_spec = BindingSpec()

    def test_configure_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.binding_spec.configure()
