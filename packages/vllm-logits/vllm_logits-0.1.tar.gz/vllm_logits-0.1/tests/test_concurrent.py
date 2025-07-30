import unittest

import src.hkkang_utils.concurrent as concurrent_utils


def count_million_and_print_name(id: int, name: str="noname") -> str:
    for _ in range(1000000):
        pass
    print(f"id: {id}, name: {name}")
    return name

class Test_concurrent(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_concurrent, self).__init__(*args, **kwargs)
    
    def test_threading(self):
        # Create threads
        threads = [concurrent_utils.Thread(count_million_and_print_name, 1, name=f"name_{i}") for i in range(10)]

        # Start threads
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Get results
        results = [thread.result for thread in threads]
        
        # Validate results
        for i, result in enumerate(results):
            self.assertEqual(result, f"name_{i}")        

    def test_multi_processing(self):
        multiprocessor = concurrent_utils.MultiProcessor(4)
        
        # Start processes
        for i in range(10):
            multiprocessor.run(count_million_and_print_name, 1, name=f"name_{i}")
        
        multiprocessor.join()
        
        # Get results
        results = multiprocessor.results

        
        # Validate results
        for i, result in enumerate(results):
            self.assertEqual(result, f"name_{i}")       


if __name__ == "__main__":
    unittest.main()
