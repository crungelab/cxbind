import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_templates import MyClassFloatDouble as MyClass


class Test(unittest.TestCase):
    def test(self):
        myclass = MyClass(1, 2)
        result = myclass.get_value()
        print(result)
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
