import unittest
from loguru import logger

from cxbind_tests.test_functions import add, sub


class Test(unittest.TestCase):
    def test(self):
        result = add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
