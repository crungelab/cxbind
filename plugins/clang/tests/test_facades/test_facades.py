import sys
from pathlib import Path

build_dir = Path(__file__).parent.parent / 'build'
sys.path.insert(0, str(build_dir))

import unittest

from cxbind_tests.test_aliases import alias_function_i, AliasClassI


class Test(unittest.TestCase):
    def test_alias_function(self):
        result = alias_function_i(1, 2)
        print(result)
        self.assertEqual(result, 3)

    def test_alias_class(self):
        myclass = AliasClassI(1)
        result = myclass.get_value()
        print(result)
        self.assertEqual(result, 1)

if __name__ == '__main__':
    unittest.main()
