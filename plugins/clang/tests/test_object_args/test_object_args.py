import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_object_args import function_with_void_arg


class Test(unittest.TestCase):
    def test_function(self):
        obj = object()
        result = function_with_void_arg(obj)
        print(result)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
