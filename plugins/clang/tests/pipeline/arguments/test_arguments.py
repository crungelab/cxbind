import unittest
from loguru import logger

from cxbind_tests.test_arguments import Arguments, in_out_function, in_out_function_with_return


class Test(unittest.TestCase):
    def test(self):
        arguments = Arguments()
        result = arguments.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

        result = in_out_function(2, 3)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 5)

        result = in_out_function_with_return(2, 3)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, (5, 5))
