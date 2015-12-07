import socket

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    HOST, PORT = "10.2.13.24", 80
    switcher = [ "NPC@fire", "NPC@electricity","NPC@leakege", "NPC@drain", "NPC@jam"]
    index = 0
    while True:
        client(HOST, PORT, switcher[index])
        index=(index+1)%5
        import time
        time.sleep(1)
