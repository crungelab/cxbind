import unittest
from loguru import logger

from cxbind_tests.test_namespace import Ns1, Ns2


class Test(unittest.TestCase):
    def test(self):
        ns1 = Ns1()
        result = ns1.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

        ns2 = Ns2()
        result = ns2.add(2, 2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)
