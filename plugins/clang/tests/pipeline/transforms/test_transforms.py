import unittest
from loguru import logger

from cxbind_tests.test_transforms import Transforms


class Test(unittest.TestCase):
    def test_handle(self):
        handle = Transforms(2)
        logger.debug(f"handle: {handle}")
        dummy = handle.create_dummy(2)
        logger.debug(f"dummy: {dummy}")
        self.assertEqual(dummy.value, 2)
