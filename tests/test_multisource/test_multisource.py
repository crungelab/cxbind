import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_multisource import Multisource1, Multisource2


class Test(unittest.TestCase):
    def test(self):
        multisource_1 = Multisource1()
        result = multisource_1.add(2, 2)
        print(result)
        self.assertEqual(result, 4)

    def test_2(self):
        multisource_2 = Multisource2()
        result = multisource_2.add(3, 3)
        print(result)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
