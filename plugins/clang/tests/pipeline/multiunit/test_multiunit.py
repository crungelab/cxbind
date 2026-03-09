import unittest
from loguru import logger

from cxbind_tests.test_multiunit import Unit1, Unit2


class Test(unittest.TestCase):
    def test(self):
        unit1 = Unit1()
        result = unit1.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

        unit2 = Unit2()
        result = unit2.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
