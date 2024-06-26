import math
from mpi4py import MPI
import numpy as np
import random
import time

LIST_SIZE = 16

def generate_data_set(size):
    return np.random.permutation(size)

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
            if (rank // 2**k) % 2 == 0:
                # Sortowanie rosnąco
                tmp.sort()
            else:
                # Sortowanie malejąco
                tmp = np.sort(tmp)[::-1] 
            half = len(tmp) // 2
            if rank < partner:
                    local_data = tmp[:half]
            else:
                local_data = tmp[half:]

            print("rank: ", rank, "|k: ", 2**k, "|j: ", j, "|local_data: ", local_data, "|partner: ", partner)
            j //= 2

        k += 1
    return local_data



def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        data = generate_data_set(LIST_SIZE)  # Rozmiar musi być potęgą dwójki
        data_to_split = []
        data = [15,12,2,1,12,2,1,6,2,1,6,7,1,6,7,14]
        for i in range(size):
            tmp = []
            for j in range (int(LIST_SIZE/size)):
                tmp.append(data[i*(LIST_SIZE//size)+j])
            data_to_split.append(tmp)
        print(data_to_split)
    else:
        data_to_split = None

    local_data = comm.scatter(data_to_split, root=0)
    # print(rank, local_data)
    local_data = bitonic_sort(local_data, comm, rank, size)
    sorted_data = comm.gather(local_data, root=0)

    if rank == 0:
        # Wypłaszczanie i czyszczenie wyniku z None (dodanych wcześniej)
        result = [x for sublist in sorted_data for x in sublist if x is not None]
        print("Posortowane dane:", result)

if __name__ == "__main__":
    main()
