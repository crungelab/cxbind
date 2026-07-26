import unittest
from loguru import logger

from cxbind_tests.test_templates import MyClassFloatDouble as MyClass, MyClassI, test_specialized


class Test(unittest.TestCase):
    def test(self):
        myclass = MyClass(1, 2)
        result = myclass.get_value()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 1)

        myclass = MyClassI(2)
        value = myclass.get_value()
        logger.debug(f"Value: {value}")
        self.assertEqual(value, 2)
        result = test_specialized(myclass)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 42)
