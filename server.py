import threading
import SocketServer
import socket
import time
import os
import csv

filedir = "input/storage1.csv"
filedir2 = "input/storage2.csv"
filepath = os.path.join(os.getcwd(), filedir)
filepath2 = os.path.join(os.getcwd(), filedir2)

# Store the paths to two file into the array
# The file in first element: read by analytic
# The file in seconde element: written by TCP_reaction
# Every time before analytic start reading, swap the position 
GLB_filepath = [filepath,filepath2]

# Mutual lock to prevent race condition
file_lock = threading.Lock()


def TCP_reaction(path, data):
    # get current time
    current = time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime())
    file_lock.acquire()
    try:
        # open csv file and append the data behind the existing data
        with open(path, 'ab') as csvfile: 
            spamwriter = csv.writer(csvfile)
            # attach a time tag for every data packet
            spamwriter.writerow([data,current])
    finally:
        file_lock.release()

def analytic():
    previous = time.time()
    while True:
        present = time.time()
        if (present - previous) >= 60:
            previous = present
            # swap the 1st and 2nd element of the array
            file_lock.acquire()
            try:
                GLB_filepath[0], GLB_filepath[1] = GLB_filepath[1],GLB_filepath[0]
            finally:
                file_lock.release()

            filepath = GLB_filepath[0]
            print "At the current analytic, the file path:", filepath
            from Analytics import run_analytic
            result = run_analytic(filepath)
            f = open(filepath, 'w')
            f.truncate()
            f.close()
            print "Analytic Domain: \n"+result
            client(SUPER_IP, SUPER_PORT, result)
        else:
            #print GLB_filepath[0]
            #print GLB_filepath[1]
            # Take a 10 sec sleep if not pass 1 min duration
            time.sleep(10) 

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        sock.sendall(message)
        response = sock.recv(1024)
    except socket.error as e:
        print "SOCKET ERROR: {}".format(e)
    finally:
        sock.close()

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = "{}: {}".format(cur_thread.name, data)
        self.request.sendall(response)
        filepath = GLB_filepath[1]
        TCP_reaction(filepath,data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "", 80
    # The supervisor's IP and port
    SUPER_IP, SUPER_PORT = "132.206.206.133",6633

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

    #Start another thread to run the analytic every 1 min
    analytic_thread = threading.Thread(target=analytic)
    analytic_thread.daemon = True
    analytic_thread.start()

    server.serve_forever()
