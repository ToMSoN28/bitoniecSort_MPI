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
    if (length & (length - 1)) == 0:  # Sprawdza, czy liczba jest potęgą dwójki
        return numbers
    else:
        next_power_of_two = 2 ** math.ceil(math.log2(length))
        additional_zeros = next_power_of_two - length
        numbers.extend([-1] * additional_zeros)  # Wstawia -1 żeby uzupełnić
    return numbers

def remove_leading_minus_ones(numbers):
    # Znajdź indeks pierwszego elementu, który nie jest -1
    first_non_minus_one_index = 0
    for number in numbers:
        if number != -1:
            break
        first_non_minus_one_index += 1
    # Przycięcie listy, usuwając wszystkie początkowe wartości -1
    return numbers[first_non_minus_one_index:]

def override_file_with_sort_list(filename, result):
    try:
        with open(filename, 'w') as file:
            numbers = [str(value) for value in result]
            file.write('\n'.join(numbers))
    except ValueError:
        print("ValueError")
        
def merge_up(arr, start, end):
    step = (end - start) // 2
    while step > 0:
        for i in range(start, end, step * 2):
            for j in range(i, i + step):
                if arr[j] > arr[j + step]:
                    arr[j], arr[j + step] = arr[j + step], arr[j]
        step //= 2

def merge_down(arr, start, end):
    step = (end - start) // 2
    while step > 0:
        for i in range(start, end, step * 2):
            for j in range(i, i + step):
                if arr[j] < arr[j + step]:
                    arr[j], arr[j + step] = arr[j + step], arr[j]
        step //= 2



def bi_sort(arr):
    n = len(arr)
    s = 2
    while s <= n:
        i = 0
        while i < n:
            if i + s <= n:
                merge_up(arr, i, i + s)
            if i + 2 * s <= n:
                merge_down(arr, i + s, i + 2 * s)
            i += s * 2
        s *= 2
    return arr


def main(file_path):
    data = read_numbers_from_file(file_path)
    print(data)
    data = adjust_list_to_power_of_two(data)
    result = bi_sort(data)
    result = remove_leading_minus_ones(result)
    print("Posortowane dane:", result)
    override_file_with_sort_list(file_path, result)

if __name__ == "__main__":
    main(sys.argv[1])
