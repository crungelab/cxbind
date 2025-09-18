import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_enums import SimpleEnum


class Test(unittest.TestCase):
    def test(self):
        self.assertEqual(SimpleEnum.VALUE_1, 0)

if __name__ == '__main__':
    unittest.main()
