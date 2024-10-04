import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_namespace import Ns1, Ns2


class Test(unittest.TestCase):
    def test(self):
        ns1 = Ns1()
        result = ns1.add(2, 2)
        self.assertEqual(result, 4)

        ns2 = Ns2()
        result = ns2.add(2, 2)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()
