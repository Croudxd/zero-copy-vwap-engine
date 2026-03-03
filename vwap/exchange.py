import socket as sk
import random
import numpy as np
from multiprocessing import Process
import multiprocessing.shared_memory as shared_memory

MCAST_GRP = '239.1.1.1'
MCAST_PORT = 5005
N_WORKERS = 3
TICKS_PER_WORKER = 10_000

data = ["SPY", "IVV", "VOO", "VTI", "QQQ"]

dtype = np.dtype([
    ('symbol', 'S8'),   # 8 bytes
    ('price',  'f8'),   # 8 bytes
    ('qty',    'f8'),   # 8 bytes
])

def generate_data(symbol, shm_name, offset, size):
    shm = shared_memory.SharedMemory(name=shm_name, create=False)
    buffer = np.ndarray(shape=(N_WORKERS * TICKS_PER_WORKER,), dtype=dtype, buffer=shm.buf)

    idx = offset  
    while True:
        price = random.uniform(670.0, 690.0)
        qty = random.uniform(0.5, 15)
        buffer[idx]['symbol'] = symbol.encode()
        buffer[idx]['price']  = price
        buffer[idx]['qty']    = qty
        idx = offset + (idx - offset + 1) % size  

def send(sock, shm_name, offset, size):
    shm = shared_memory.SharedMemory(name=shm_name, create=False)
    buffer = np.ndarray(shape=(N_WORKERS * TICKS_PER_WORKER,), dtype=dtype, buffer=shm.buf)

    idx = offset  
    while True:
        sock.sendto(bytes(buffer[idx]), (MCAST_GRP, MCAST_PORT))  
        idx = offset + (idx - offset + 1) % size  

def create_shm():
    shm = shared_memory.SharedMemory(create=True, size=dtype.itemsize * TICKS_PER_WORKER * N_WORKERS)
    buffer = np.ndarray(shape=(N_WORKERS * TICKS_PER_WORKER,), dtype=dtype, buffer=shm.buf)
    return shm, buffer  

def main():
    sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM, sk.IPPROTO_UDP)
    sock.setsockopt(sk.IPPROTO_IP, sk.IP_MULTICAST_IF, sk.inet_aton("127.0.0.1"))
    sock.setsockopt(sk.IPPROTO_IP, sk.IP_MULTICAST_LOOP, 1)

    shm, buffer = create_shm()

    worker_0_offset = 0
    worker_1_offset = 10_000
    worker_2_offset = 20_000

    p0_gen  = Process(target=generate_data, args=(data[0], shm.name, worker_0_offset, TICKS_PER_WORKER))
    p1_gen  = Process(target=generate_data, args=(data[1], shm.name, worker_1_offset, TICKS_PER_WORKER))
    p2_gen  = Process(target=generate_data, args=(data[2], shm.name, worker_2_offset, TICKS_PER_WORKER))

    p0_send = Process(target=send, args=(sock, shm.name, worker_0_offset, TICKS_PER_WORKER))
    p1_send = Process(target=send, args=(sock, shm.name, worker_1_offset, TICKS_PER_WORKER))
    p2_send = Process(target=send, args=(sock, shm.name, worker_2_offset, TICKS_PER_WORKER))

    p0_gen.start()
    p1_gen.start()
    p2_gen.start()

    p0_send.start()
    p1_send.start()
    p2_send.start()

    p0_gen.join()
    p1_gen.join()
    p2_gen.join()

    p0_send.join()
    p1_send.join()
    p2_send.join()

    shm.close()
    shm.unlink()

if __name__ == "__main__":
    main()
