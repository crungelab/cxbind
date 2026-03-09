import unittest
from loguru import logger

from cxbind_tests.test_inits import Inits, KwInits, KwInitsUse, ArgsInits


class Test(unittest.TestCase):
    def test_init(self):
        inits = Inits(2)
        result = inits.add(2)
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 4)

    def test_kw_init(self):
        kw_inits = KwInits(a=2, b=3)
        result = kw_inits.add()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 5)

    def test_kw_init_use(self):
        kw_inits = KwInitsUse(a=2, b=3)
        result = kw_inits.add()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 5)
        self.assertEqual(kw_inits.c, 3)

    def test_args_init(self):
        args_inits = ArgsInits(2, 3)
        result = args_inits.add()
        logger.debug(f"Result: {result}")
        self.assertEqual(result, 5)
