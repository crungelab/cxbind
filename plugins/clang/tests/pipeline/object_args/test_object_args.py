import unittest
from loguru import logger

from cxbind_tests.test_object_args import function_with_void_arg


class Test(unittest.TestCase):
    def test_function(self):
        obj = object()
        result = function_with_void_arg(obj)
        logger.debug(f"Result: {result}")
        self.assertIsNone(result)
