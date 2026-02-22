import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_repr import Repr


class Test(unittest.TestCase):
    def test_repr(self):
        repr = Repr(2)
        print(repr)
        result = repr.add(2)
        print(result)
        self.assertEqual(result, 4)


if __name__ == '__main__':
    unittest.main()
