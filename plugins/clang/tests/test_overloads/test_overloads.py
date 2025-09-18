import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_overloads import Overloads


class Test(unittest.TestCase):
    def test(self):
        overloads = Overloads()
        result = overloads.add(2, 2)
        print(result)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()
