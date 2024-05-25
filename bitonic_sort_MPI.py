import math
import sys
from mpi4py import MPI
import numpy as np


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
        
def bitonic_merge_reku(arr, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            if direction == (arr[i] > arr[i + k]):
                arr[i], arr[i + k] = arr[i + k], arr[i]
        bitonic_merge_reku(arr, low, k, direction)
        bitonic_merge_reku(arr, low + k, k, direction)

def bitonic_sort_reku(arr, low, cnt, direction):
    if cnt > 1:
        k = cnt // 2
        bitonic_sort_reku(arr, low, k, True)  # Sort in ascending order
        bitonic_sort_reku(arr, low + k, k, False)  # Sort in descending order
        bitonic_merge_reku(arr, low, cnt, direction)
        
def merge_up_iter(arr, start, end):
    step = (end - start) // 2
    while step > 0:
        for i in range(start, end, step * 2):
            for j in range(i, i + step):
                if arr[j] > arr[j + step]:
                    arr[j], arr[j + step] = arr[j + step], arr[j]
        step //= 2

def merge_down_iter(arr, start, end):
    step = (end - start) // 2
    while step > 0:
        for i in range(start, end, step * 2):
            for j in range(i, i + step):
                if arr[j] < arr[j + step]:
                    arr[j], arr[j + step] = arr[j + step], arr[j]
        step //= 2

def bitonic_sort_iter(arr):
    n = len(arr)
    s = 2
    while s <= n:
        i = 0
        while i < n:
            if i + s <= n:
                merge_up_iter(arr, i, i + s)
            if i + 2 * s <= n:
                merge_down_iter(arr, i + s, i + 2 * s)
            i += s * 2
        s *= 2
    return arr

def type_sort(arr, type):
    if type == "iter":
        # use iter b_sort
        bitonic_sort_iter(arr)
    else:    
        # use reku b_sort
        bitonic_sort_reku(arr, 0, len(arr), True)
    
    
def merge(arr, direction_up, type):
    if direction_up:
        if type == "iter":
            merge_up_iter(arr, 0, len(arr))
        else:
            bitonic_merge_reku(arr, 0, len(arr), direction_up)
    else:
        if type == "iter":
            merge_down_iter(arr, 0, len(arr))
        else:
            bitonic_merge_reku(arr, 0, len(arr), direction_up)

def bitonic_sort(data, comm, rank, size, type):
    direction = rank%2 == 0
    type_sort(data, type)
    if not direction:
        data.reverse()
    if rank == 0:
        print(rank, data, len(data))
    n = 0
    while 2**n < size:    
    # for n in range(1,size): #TUTAJ zmodyfikowac na procesy
        partner = rank^(2**n)    # zweryfikować partnerów bo coś nie tak działa
        if rank > partner:
            comm.send(data, dest=partner)
        else:
            recv_data = comm.recv(source=partner)
            data = np.concatenate((data, recv_data))
        
            merge_directition = (rank/(2**(n+1)))%2 == 0
            print(rank, partner, len(data))
            merge(data, merge_directition, type)
        n += 1
    return data
            
def main(file_path, alg):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        data_to_split = []
        data = read_numbers_from_file(file_path)
        data = adjust_list_to_power_of_two(data)
        print(len(data))
        for i in range(size):
            tmp = []
            for j in range (int(len(data)/size)):
                tmp.append(data[i*(len(data)//size)+j])
            data_to_split.append(tmp)
    else:
        data_to_split = None

    local_data = comm.scatter(data_to_split, root=0)
    if alg not in ('iter', 'reku'):    
        result = bitonic_sort(local_data, comm, rank, size, "iter")
    else:
        result = bitonic_sort(local_data, comm, rank, size, "iter")

    if rank == 0:
        if alg not in ('iter', 'reku'):
            print('Implemnetacja iteracyjna w wątkach')
        result = remove_leading_minus_ones(result)
        print("Posortowane dane:", result)
    #     override_file_with_sort_list(file_path, result)

if __name__ == "__main__":

    main(sys.argv[1], sys.argv[2])
