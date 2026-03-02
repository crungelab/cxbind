import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_callbacks import function_with_callback


class Test(unittest.TestCase):
    def test__function(self):
        def callback(x, context):
            print(x)

        result = function_with_callback([1, 2, 3], callback, None)
        print(result)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
