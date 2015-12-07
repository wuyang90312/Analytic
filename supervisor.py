import threading
import SocketServer
import time
import os
import csv

#filedir = "input/email2.csv"
#filepath = os.path.join(os.getcwd(), filedir)


#def TCP_reaction(path, data):
    # open csv file and append the data behind the existing data
#    with open(path, 'ab') as csvfile:
#        spamwriter = csv.writer(csvfile)
        # attach a time tag for every data
#        current = time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime())
#        spamwriter.writerow([data,current])

#def analytic():
#    while True:
#        print "I am running Analytic"
#        time.sleep(60)

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        print data
        #cur_thread = threading.current_thread()
        #response = "{}: {}".format(cur_thread.name, data)
        #self.request.sendall(response)
        #TCP_reaction(filepath,data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "", 6633 #80

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
    #analytic_thread = threading.Thread(target=analytic)
    #analytic_thread.daemon = True
    #analytic_thread.start()

    server.serve_forever()
