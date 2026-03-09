import unittest
from loguru import logger

from cxbind_tests.test_enums import SimpleEnum


class Test(unittest.TestCase):
    def test(self):
        logger.debug(f"SimpleEnum.VALUE_1: {SimpleEnum.VALUE_1}")
        self.assertEqual(SimpleEnum.VALUE_1, 0)
