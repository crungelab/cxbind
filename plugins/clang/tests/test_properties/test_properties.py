import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_properties import Properties


class Test(unittest.TestCase):
    def test(self):
        obj = Properties()
        obj.set_x(10)
        self.assertEqual(obj.get_x(), 10)
        self.assertEqual(obj.x, 10)

        self.assertEqual(obj.y, 11)

        print(obj.x)
        print(obj.y)

if __name__ == '__main__':
    unittest.main()
