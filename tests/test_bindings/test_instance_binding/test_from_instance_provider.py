import unittest

from opyoid.bindings import FromInstanceProvider


class TestFromInstanceProvider(unittest.TestCase):
    def setUp(self):
        self.instance = object()
        self.provider = FromInstanceProvider(self.instance)

    def test_get(self):
        provided_instance = self.provider.get()
        self.assertIs(self.instance, provided_instance)
