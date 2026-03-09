import unittest
from loguru import logger

from cxbind_tests.test_multisource import Multisource1, Multisource2


class Test(unittest.TestCase):
    def test(self):
        multisource_1 = Multisource1()
        result = multisource_1.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

    def test_2(self):
        multisource_2 = Multisource2()
        result = multisource_2.add(3, 3)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 6)
