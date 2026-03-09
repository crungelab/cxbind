import unittest
from loguru import logger

from cxbind_tests.test_wrappers import wrapper_in_fn, wrapper_out_fn, capsule_in_fn, capsule_out_fn

# TODO: Need to add tests for wrapper functions

class Test(unittest.TestCase):
    def test(self):
        logger.debug(f"wrapper_in_fn: {wrapper_in_fn}")
        logger.debug(f"wrapper_out_fn: {wrapper_out_fn}")
        logger.debug(f"capsule_in_fn: {capsule_in_fn}")
        logger.debug(f"capsule_out_fn: {capsule_out_fn}")
        self.assertIsNotNone(wrapper_in_fn)
        self.assertIsNotNone(wrapper_out_fn)
        self.assertIsNotNone(capsule_in_fn)
        self.assertIsNotNone(capsule_out_fn)
