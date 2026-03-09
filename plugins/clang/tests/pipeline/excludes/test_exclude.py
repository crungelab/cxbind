import unittest
from loguru import logger

from cxbind_tests.test_exclude import Exclude


class Test(unittest.TestCase):
    def test(self):
        exclude = Exclude()
        result = exclude.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
