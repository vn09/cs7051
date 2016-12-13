import socket
import threading
import SocketServer
from SocketServer import ThreadingMixIn
from Queue import Queue
import os
import argparse

STUDENT_ID = "16314667"
HOST = "localhost"
PORT = 8080

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    data = self.request.recv(1024)
    cur_thread = threading.current_thread()
    print("{}: {}".format(cur_thread.name, data))
    print(self.client_address)
    msgs = data.split()

    # Serve client based on the data server received
    if msgs[0] == "KILL_SERVICE":
      # Kill system
      os._exit(1)

    if msgs[0] == "HELO":
      print("Receiving HELO message from client: (%s, %s)" % self.client_address)
      response = "{}IP:{}\nPort:{}\nStudentID:{}\n".format(data, HOST, PORT, STUDENT_ID)
      self.request.sendall(response)
    else:
      pass


class ThreadPoolMixIn(ThreadingMixIn):
  """Use a thread pool instead of a new thread on every request"""

  num_of_thread = 5
  allow_reuse_address = True

  def set_number_thread(self, num_threads):
    self.num_of_thread = num_threads

  def serve_forever(self):
    """Handle one request at a time until doomsday."""

    # set up the threadpool
    self.requests = Queue(self.num_of_thread)

    for x in range(self.num_of_thread):
      t = threading.Thread(target=self.process_request_thread)
      t.setDaemon(1)
      t.start()

    # server main loop
    while True:
      self.handle_request()

    self.server_close()

  def process_request_thread(self):
    """Obtain request from queue instead of directly from server socket"""
    while True:
      ThreadingMixIn.process_request_thread(self, *self.requests.get())

  def handle_request(self):
    """Use a thread pool instead of a new thread on every request"""
    try:
      request, client_address = self.get_request()
    except socket.error:
      return
    if self.verify_request(request, client_address):
      # Register request to queue
      self.requests.put((request, client_address))


class ThreadedTCPServer(ThreadPoolMixIn, SocketServer.TCPServer):
  pass


def main():
  global PORT
  parser = argparse.ArgumentParser(description='Argument to run server')
  parser.add_argument('--p', action = "store", dest="p", type=int,
                    help='an integer for the accumulator')

  args = parser.parse_args()
  PORT = args.port

  server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

  # Init 10 threads
  server.set_number_thread(10)

  # Start a thread with the server -- that thread will then start one
  # more thread for each request
  server_thread = threading.Thread(target=server.serve_forever)
  server_thread.start()

  print("Server starts at (%s, %s)" % (HOST, PORT))


if __name__ == "__main__":
  main()
