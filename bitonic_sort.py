from mpi4py import MPI
import numpy as np
import random
import time

LIST_SIZE = 16

def generate_data_set(size):
    return np.random.permutation(size)

def bitonic_sort(data, comm, rank, size):
    # comm = MPI.COMM_WORLD
    # rank = comm.Get_rank()
    # size = comm.Get_size()

    local_n = len(data)

    total_n = LIST_SIZE
    local_data = data
    for k in range(2, total_n, 2):
        for j in range(k//2, 0, -1):
            # for i in range(0, total_n, k):
                # if (i // k) % 2 == 0:
                #     direction = 1
                # else:
                #     direction = 0

                partner = rank ^ j
                
                comm.send(local_data, dest=partner)
                recv_data = comm.recv(source=partner)
                
                # tmp = local_data + recv_data
                # tmp.sort(reverse=(rank // k) % 2 != 0)
                # half = len(tmp) // 2
                # local_data = tmp[:half] if rank < partner else tmp[half:]

                tmp = np.concatenate((local_data, recv_data))
                if (rank // k) % 2 == 0:
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

                # if rank == 0:
                    print("rank: ", rank, "|k: ", k, "|j: ", j, "|local_data: ", local_data, "|partner: ", partner)

                # data[i:i+j*2] = merged_data
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
