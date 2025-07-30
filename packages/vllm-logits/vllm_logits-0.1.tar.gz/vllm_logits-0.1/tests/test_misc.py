import unittest

import src.hkkang_utils.misc as misc_utils


class Test_misc_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_misc_utils, self).__init__(*args, **kwargs)
    
    def test_infinit_iterator(self):
        input_list = [1,2,3,4,5]
        result = []
        for i, item in enumerate(misc_utils.infinite_iterator(input_list)):
            if i == 10:
                break
            result.append(item)
        gold = [1,2,3,4,5,1,2,3,4,5]
        self.assertEqual(result, gold, f"result: {result}, gold: {gold}")
    
    def test_to_dict(self):
        class TmpObject():
            def __init__(self, a,b,c,d,e):
                self.a=a
                self.b=b
                self._c=c
                self.__d=d
                self.private_e=e
        tmp = TmpObject(1,2,3,4,5)   
        tmp_dict = misc_utils.to_dict(tmp, exclude_prefixes=["_", "__", "private"]) 
        self.assertEqual(type(tmp_dict), dict)
        self.assertDictEqual(tmp_dict, {"a":1, "b":2})
    
if __name__ == "__main__":
    unittest.main()
    
    