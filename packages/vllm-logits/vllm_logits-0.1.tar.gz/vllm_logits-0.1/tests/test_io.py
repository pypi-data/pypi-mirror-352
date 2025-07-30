import unittest

import src.hkkang_utils.io as io_utils

class Test_io(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_io, self).__init__(*args, **kwargs)
    
    def _inner_func(self, *args, **kwargs):
        print(f"Inner function called with args: {args} and kwargs: {kwargs}")
    
    def test_io(self):
        output = io_utils.intercept_stdout(self._inner_func)(1, 2, 3, a=4, b=5, c=6)
        self.assertTrue(output.startswith("Inner function called with args: "))
        print(f"Test passed! Output: {output}")

if __name__ == "__main__":
    unittest.main()
