import math
import sys
from mpi4py import MPI
import numpy as np
import random
import time

def read_numbers_from_file(filename):
    with open(filename, 'r') as file:
        numbers = [int(line.strip()) for line in file.readlines()]
    return numbers

def adjust_list_to_power_of_two(numbers):
    length = len(numbers)
    if (length & (length - 1)) == 0:
        return numbers
    else:
        next_power_of_two = 2 ** math.ceil(math.log2(length))
        additional_zeros = next_power_of_two - length
        numbers.extend([-1] * additional_zeros)
    return numbers

def remove_leading_minus_ones(numbers):
    first_non_minus_one_index = 0
    for number in numbers:
        if number != -1:
            break
        first_non_minus_one_index += 1
    return numbers[first_non_minus_one_index:]

def override_file_with_sort_list(filename, result):
    try:
        with open(filename, 'w') as file:
            numbers = [str(value) for value in result]
            file.write('\n'.join(numbers))
    except ValueError:
        print("ValueError")
        

def bitonic_merge(arr, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            if direction == (arr[i] > arr[i + k]):
                arr[i], arr[i + k] = arr[i + k], arr[i]
        bitonic_merge(arr, low, k, direction)
        bitonic_merge(arr, low + k, k, direction)

def bitonic_sort(arr, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        bitonic_sort(arr, low, k, True)
        bitonic_sort(arr, low + k, k, False)
        bitonic_merge(arr, low, cnt, direction)

def b_sort(arr, ascending=True):
    arr = bitonic_sort(arr, 0, len(arr), ascending)
    return arr

def main(file_path):
    data = read_numbers_from_file(file_path)
    print(data)
    data = adjust_list_to_power_of_two(data)
    bitonic_sort(data, 0 , len(data), True)
    data = remove_leading_minus_ones(data)
    print("Posortowane dane:", data)
    # override_file_with_sort_list(file_path, result)

if __name__ == "__main__":
    main(sys.argv[1])
