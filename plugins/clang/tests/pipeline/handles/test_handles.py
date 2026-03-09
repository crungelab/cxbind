import unittest
from loguru import logger

from cxbind_tests.test_handles import Handle


class Test(unittest.TestCase):
    def test_handle(self):
        handle = Handle(2)
        logger.debug(f"Handle: {handle}")
        dummy = handle.create_dummy(2)
        logger.debug(f"Dummy: {dummy}")
        self.assertEqual(dummy.value, 2)
