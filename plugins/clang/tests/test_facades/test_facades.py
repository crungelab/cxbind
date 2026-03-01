import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_facades import facade_function


class Test(unittest.TestCase):
    def test_facade_function(self):
        result = facade_function([1, 2, 3])
        print(result)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
