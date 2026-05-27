from typing import List

def bubble_sort(arr: List[int]) -> List[int]:
    """
    Sorts a list of integers using the bubble sort algorithm with early exit optimization.
    
    Args:
        arr: A list of integers to be sorted.
        
    Returns:
        The sorted list of integers.
    """
    n = len(arr)
    # Outer loop for each pass
    for i in range(n):
        swapped = False
        # Inner loop for comparisons in the unsorted portion
        # After each pass, the largest i elements are already in place
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                # Swap elements if they are in the wrong order
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no two elements were swapped by inner loop, then break (Early Exit)
        if not swapped:
            break
            
    return arr
