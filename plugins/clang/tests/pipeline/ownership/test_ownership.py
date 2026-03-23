import unittest
from loguru import logger

from cxbind_tests.test_overloads import Overloads


class Test(unittest.TestCase):
    def test(self):
        overloads = Overloads()

        result = overloads.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

        result = overloads.add(2.0, 2.0)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4.0)
