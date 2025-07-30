import unittest

import src.hkkang_utils.list as list_utils


class Test_list_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_list_utils, self).__init__(*args, **kwargs)

    def test_do_flatten_list(self):
        input_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        gold = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        result = list_utils.do_flatten_list(input_list)
        self.assertEqual(result, gold, f"result: {result}, gold_after: {gold}")

    def test_map_many(self):
        input_list = [1, 2, 3, 4, 5]
        functions = [lambda x: x + 1, lambda x: x * 2]
        gold = [4, 6, 8, 10, 12]
        result = list_utils.map_many(functions, input_list)
        self.assertEqual(result, gold, f"result: {result}, gold: {gold}")

    def test_get(self):
        input_list = [1, 2, 3, 4, 5]
        result1 = list_utils.get(input_list, 3, 0)
        gold1 = 4
        result2 = list_utils.get(input_list, 10, 0)
        gold2 = 0
        result3 = list_utils.get(input_list, -1, 0)
        gold3 = 0
        self.assertEqual(result1, gold1, f"result1: {result1}, gold1: {gold1}")
        self.assertEqual(result2, gold2, f"result2: {result2}, gold2: {gold2}")
        self.assertEqual(result3, gold3, f"result3: {result3}, gold3: {gold3}")

    def test_divide_into_chunks(self):
        item1 = list(range(10))
        pred = list_utils.divide_into_chunks(item1, 4)
        gold1 = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        # Validate results
        self.assertEqual(pred, gold1, f"pred: {pred}, gold1: {gold1}")

    def test_chunks(self):
        item1 = list(range(10))
        pred = list(list_utils.chunks(item1, 3))
        gold1 = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        # Validate results
        self.assertEqual(pred, gold1, f"pred: {pred}, gold1: {gold1}")


if __name__ == "__main__":
    unittest.main()
