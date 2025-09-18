import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_multiunit import Unit1, Unit2


class Test(unittest.TestCase):
    def test(self):
        unit1 = Unit1()
        result = unit1.add(2, 2)
        self.assertEqual(result, 4)

        unit2 = Unit2()
        result = unit2.add(2, 2)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()
