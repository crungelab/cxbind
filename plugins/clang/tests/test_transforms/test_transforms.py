import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_handles import Handle


class Test(unittest.TestCase):
    def test_handle(self):
        handle = Handle(2)
        print(handle)
        dummy = handle.create_dummy(2)
        print(dummy)
        self.assertEqual(dummy.value, 2)


if __name__ == '__main__':
    unittest.main()
