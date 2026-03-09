import unittest
from loguru import logger

from cxbind_tests.test_defaults import Defaults


class Test(unittest.TestCase):
    def test(self):
        simple = Defaults()
        result = simple.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
