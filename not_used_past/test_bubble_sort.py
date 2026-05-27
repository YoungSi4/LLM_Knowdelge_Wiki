import unittest
from bubble_sort import bubble_sort

class TestBubbleSort(unittest.TestCase):
    def test_normal_case(self):
        self.assertEqual(bubble_sort([5, 2, 9, 1, 5, 6]), [1, 2, 5, 5, 6, 9])

    def test_empty_list(self):
        self.assertEqual(bubble_sort([]), [])

    def test_single_element(self):
        self.assertEqual(bubble_sort([1]), [1])

    def test_already_sorted(self):
        self.assertEqual(bubble_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        self.assertEqual(bubble_sort([5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])

    def test_with_negatives(self):
        self.assertEqual(bubble_sort([-2, 45, 0, 11, -9]), [-9, -2, 0, 11, 45])

if __name__ == "__main__":
    unittest.main()
