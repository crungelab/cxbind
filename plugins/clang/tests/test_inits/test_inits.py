import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_inits import Inits, KwInits


class Test(unittest.TestCase):
    def test_init(self):
        inits = Inits(2)
        result = inits.add(2)
        print(result)
        self.assertEqual(result, 4)

    def test_kw_init(self):
        kw_inits = KwInits(a=2, b=3)
        result = kw_inits.add()
        print(result)
        self.assertEqual(result, 5)

if __name__ == '__main__':
    unittest.main()
