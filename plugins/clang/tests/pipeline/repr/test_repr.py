import unittest
from loguru import logger

from cxbind_tests.test_repr import Repr


class Test(unittest.TestCase):
    def test_repr(self):
        repr = Repr(2)
        logger.debug(f"repr: {repr}")
        result = repr.add(2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
