import unittest
from loguru import logger

from cxbind_tests.test_facades import vector_facade_function


class Test(unittest.TestCase):
    def test_facade_function(self):
        result = vector_facade_function([1, 2, 3])
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 6)
