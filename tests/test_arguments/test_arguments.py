import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_arguments import Arguments


class Test(unittest.TestCase):
    def test(self):
        arguments = Arguments()
        result = arguments.add(2, 2)
        print(result)
        self.assertEqual(result, 4)

if __name__ == '__main__':
    unittest.main()
