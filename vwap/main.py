import socket as sk
import struct
import multiprocessing
import multiprocessing.pool as Pool
import multiprocessing.shared_memory as shm

def sock_connect():
    MCAST_GRP = '239.1.1.1'
    MCAST_PORT = 5005
    IS_ALL_GROUPS = True

    sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM, sk.IPPROTO_UDP)
    sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))

    mreq = struct.pack("4s4s", sk.inet_aton(MCAST_GRP), sk.inet_aton("127.0.0.1"))

    sock.setsockopt(sk.IPPROTO_IP, sk.IP_ADD_MEMBERSHIP, mreq)
    return sock

def sbe_decode(sbe):
    symbol = sbe[0:3].decode('utf-8')
    price = struct.unpack('d', sbe[8:16])[0]
    qty = struct.unpack('d', sbe[16:24])[0]
    return symbol, price, qty


def main():
    sock = sock_connect()

    count = 0
    while True:
        sbe_decode(sock.recv(10240))
        count+=1
        print(count)
    


if __name__ == "__main__":
    main()
