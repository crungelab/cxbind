import unittest
from loguru import logger

from cxbind_tests.test_advanced import Advanced


class Test(unittest.TestCase):
    def test(self):
        advanced = Advanced(2)
        
        result = advanced.add(2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

        result = advanced.add(4)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 6)
