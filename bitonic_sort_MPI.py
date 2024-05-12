import math
import sys
from mpi4py import MPI
import numpy as np
import random
import time

LIST_SIZE = 16

def generate_data_set(size):
    return np.random.permutation(size)

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
        
def custom_sort(array, ascending=True):
    sorted_array = []
    array = array.tolist()
    while len(array)>0:
        if ascending:
            value = min(array)
        else:
            value = max(array)
        sorted_array.append(value)
        array.remove(value)
    return sorted_array

def bitonic_sort(data, comm, rank, size):

    total_n = len(data)*size
    local_data = data
    k = 1
    while 2**k < size + 1:
        j = 2**k // 2
        while j > 0:

            partner = rank ^ j
                
            # wymiana danych z partnerem
            comm.send(local_data, dest=partner)
            recv_data = comm.recv(source=partner)
                

            tmp = np.concatenate((local_data, recv_data))
            tmp = custom_sort(tmp, (rank // 2**k) % 2 == 0)
            half = len(tmp) // 2
            if rank < partner:
                    local_data = tmp[:half]
            else:
                local_data = tmp[half:]

            # print("rank: ", rank, "|k: ", 2**k, "|j: ", j, "|local_data: ", local_data, "|partner: ", partner)
            j //= 2

        k += 1
    return local_data



def main(file_path):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        data_to_split = []
        data = read_numbers_from_file(file_path)
        print(data)
        data = adjust_list_to_power_of_two(data)
        
        for i in range(size):
            tmp = []
            for j in range (int(len(data)/size)):
                tmp.append(data[i*(len(data)//size)+j])
            data_to_split.append(tmp)
        # print(data_to_split)
    else:
        data_to_split = None

    local_data = comm.scatter(data_to_split, root=0)
    # print(rank, local_data)
    local_data = bitonic_sort(local_data, comm, rank, size)
    sorted_data = comm.gather(local_data, root=0)

    if rank == 0:
        # Wypłaszczanie i czyszczenie wyniku z None (dodanych wcześniej)
        result = [x for sublist in sorted_data for x in sublist if x is not None]
        result = remove_leading_minus_ones(result)
        print("Posortowane dane:", result)
        override_file_with_sort_list(file_path, result)

if __name__ == "__main__":
    main(sys.argv[1])
