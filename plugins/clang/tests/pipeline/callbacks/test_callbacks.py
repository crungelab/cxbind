import unittest
from loguru import logger

from cxbind_tests.test_callbacks import function_with_callback


class Test(unittest.TestCase):
    def test__function(self):
        def callback(x):
            logger.debug(f"x: {x}")

        function_with_callback([1, 2, 3], callback)
