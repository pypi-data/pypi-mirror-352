import time as time_module
import unittest
from typing import List, Tuple

import src.hkkang_utils.time as time_utils

TEST_TIME = 2


class Test_time_utils(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_time_utils, self).__init__(*args, **kwargs)

    def test_timer_measure(self):
        timer = time_utils.Timer()
        timer.start()
        time_module.sleep(TEST_TIME)
        timer.stop()
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."

    def test_timer_measure_using_with(self):
        timer = time_utils.Timer()
        with timer.measure():
            time_module.sleep(TEST_TIME)
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."

    def test_timer_singleton_by_name1(self):
        def test_func():
            timer = time_utils.Timer()
            with timer.measure():
                time_module.sleep(TEST_TIME)

        test_func()
        timer = time_utils.Timer(
            class_name="Test_time_utils",
            func_name="test_timer_singleton_by_name1.test_func",
        )
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."

    def test_timer_singleton_by_name2(self):
        timer = time_utils.Timer()
        with timer.measure():
            time_module.sleep(TEST_TIME)

        timer = time_utils.Timer(
            class_name="Test_time_utils",
            func_name="test_timer_singleton_by_name2",
        )
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."

    def test_timer_decorator(self):
        @time_utils.measure_time
        def test_func():
            time_module.sleep(TEST_TIME)

        test_func()
        timer = time_utils.Timer(
            class_name="Test_time_utils", func_name="test_timer_decorator.test_func"
        )
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."

    def test_timer_measure_total_elapsed_time(self):
        timer = time_utils.Timer()
        with timer.measure():
            time_module.sleep(TEST_TIME)
        with timer.measure():
            time_module.sleep(TEST_TIME)
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."
        self.assertTrue(
            timer.total_elapsed_time > TEST_TIME * 2
            and timer.total_elapsed_time < (TEST_TIME * 2 + 1),
            f"Timer is not working properly: {timer.total_elapsed_time} sec is measured.",
        )
        timer.show_total_elapsed_time()

    def test_timer_measure_avg_elapsed_time(self):
        timer = time_utils.Timer()
        with timer.measure():
            time_module.sleep(TEST_TIME)
        with timer.measure():
            time_module.sleep(TEST_TIME)
        self.assertTrue(
            timer.elapsed_time > TEST_TIME and timer.elapsed_time < TEST_TIME + 1
        ), f"Timer is not working properly: {timer.elapsed_time} sec is measured."
        self.assertTrue(
            timer.avg_elapsed_time > TEST_TIME
            and timer.avg_elapsed_time < (TEST_TIME + 1),
            f"Timer is not working properly: {timer.avg_elapsed_time} sec is measured.",
        )
        timer.show_avg_elapsed_time()


class Test_time_utils2(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_time_utils2, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        timer1 = time_utils.Timer(func_name="test_timer_summary1")
        timer2 = time_utils.Timer(func_name="test_timer_summary2")
        # Measure time
        with timer1.measure():
            time_module.sleep(TEST_TIME)
        with timer1.measure():
            time_module.sleep(TEST_TIME)
        with timer2.measure():
            time_module.sleep(TEST_TIME)
        with timer2.measure():
            time_module.sleep(TEST_TIME)

    def test_timer_summary_for_single_instance(self):
        timer = time_utils.Timer(func_name="test_timer_summary1")
        # Get statistics
        fname, call_cnt, avg_time, total_time = timer.summarize_measured_time()
        # Check
        self.assertEqual(fname, "test_timer_summary1")
        self.assertEqual(call_cnt, 2)
        self.assertGreater(avg_time, TEST_TIME)
        self.assertLess(avg_time, TEST_TIME + 1)
        self.assertGreater(total_time, TEST_TIME * 2)
        self.assertLess(total_time, TEST_TIME * 2 + 1)

    def test_timer_summary_for_all_instances(self):
        infos: List[
            Tuple[str, int, float, float]
        ] = time_utils.Timer.summarize_measured_times()
        fnames = list(map(lambda k: k[0], infos))
        self.assertGreaterEqual(len(infos), 2)
        self.assertIn("test_timer_summary1", fnames)
        test_timer_summary1_idx = fnames.index("test_timer_summary1")
        self.assertEqual(infos[test_timer_summary1_idx][1], 2)
        self.assertGreater(infos[test_timer_summary1_idx][2], TEST_TIME)
        self.assertLess(infos[test_timer_summary1_idx][2], TEST_TIME + 1)
        self.assertGreater(infos[test_timer_summary1_idx][3], TEST_TIME * 2)
        self.assertLess(infos[test_timer_summary1_idx][3], TEST_TIME * 2 + 1)
        self.assertIn("test_timer_summary2", fnames)
        test_timer_summary2_idx = fnames.index("test_timer_summary2")
        self.assertEqual(infos[test_timer_summary2_idx][1], 2)
        self.assertGreater(infos[test_timer_summary2_idx][2], TEST_TIME)
        self.assertLess(infos[test_timer_summary2_idx][2], TEST_TIME + 1)
        self.assertGreater(infos[test_timer_summary2_idx][3], TEST_TIME * 2)
        self.assertLess(infos[test_timer_summary2_idx][3], TEST_TIME * 2 + 1)


if __name__ == "__main__":
    unittest.main()
