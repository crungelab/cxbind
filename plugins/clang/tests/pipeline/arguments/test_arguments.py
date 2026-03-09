import unittest
from loguru import logger

from cxbind_tests.test_arguments import Arguments


class Test(unittest.TestCase):
    def test(self):
        arguments = Arguments()
        result = arguments.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
