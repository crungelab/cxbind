import unittest
from loguru import logger

from cxbind_tests.test_templates import MyClassFloatDouble as MyClass


class Test(unittest.TestCase):
    def test(self):
        myclass = MyClass(1, 2)
        result = myclass.get_value()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 1)
