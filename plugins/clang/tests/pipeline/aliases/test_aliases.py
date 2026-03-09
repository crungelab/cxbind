import unittest
from loguru import logger

from cxbind_tests.test_aliases import alias_function_i, AliasClassI


class Test(unittest.TestCase):
    def test_alias_function(self):
        result = alias_function_i(1, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 3)

    def test_alias_class(self):
        myclass = AliasClassI(1)
        result = myclass.get_value()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 1)
