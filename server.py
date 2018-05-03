from config import *
import socket

def main():
    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    listen_addr = ("192.168.43.200",5005)
    UDPSock.bind(listen_addr)
    print("Server running")
    while True:
        print("Waiting for data")
        data, addr = UDPSock.recvfrom(1024)
        print("Got: {} from {}".format(data, addr))


if __name__ == "__main__":
    main()