from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    for i in range(1, size):
        data = comm.recv(source = i)
        print "P0 received data=", data, "from processor", i
else:
    data = rank
    comm.send(data, dest=0)
