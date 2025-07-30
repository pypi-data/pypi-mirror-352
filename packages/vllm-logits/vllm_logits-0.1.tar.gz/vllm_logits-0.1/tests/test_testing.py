import os
import unittest

import src.hkkang_utils.testing as test_utils

TEST_DIR_PATH = "test_dir"


class Test_test_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_test_utils, self).__init__(*args, **kwargs)
    
    @test_utils.set_and_clean_test_dir(TEST_DIR_PATH)
    def _func_to_be_decorated(self):
        # Check if directory exists
        self.assertTrue(os.path.exists(TEST_DIR_PATH))
    
    def test_decorator(self):
        # Make sure that the directory does not exists
        self.assertFalse(os.path.exists(TEST_DIR_PATH))
        # Check if the decorator works
        self._func_to_be_decorated()
        # Check if directory is removed
        self.assertFalse(os.path.exists(TEST_DIR_PATH))

if __name__ == "__main__":
    unittest.main()
