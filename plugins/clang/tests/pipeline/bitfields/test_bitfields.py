import unittest
from loguru import logger

from cxbind_tests.test_properties import Properties


class Test(unittest.TestCase):
    def test(self):
        obj = Properties()
        obj.set_x(10)


        logger.debug(f"x: {obj.x}")
        logger.debug(f"y: {obj.y}")

        self.assertEqual(obj.get_x(), 10)
        self.assertEqual(obj.x, 10)
        self.assertEqual(obj.y, 11)
