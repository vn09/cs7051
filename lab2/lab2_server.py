#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import thread
import argparse
import struct
import fcntl


class Client:
  def __init__(self, session):
    self.connection = session[0]
    self.address = session[1]

  def send(self, msg):
    self.send_raw(str(msg))

  def send_raw(self, msg):
    self.connection.send(msg)

  def get_session(self):
    return self.connection


class Server:
  def __init__(self, port):
    self.port = port
    self.clients = list()
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.student_id = "16314667"
    self._set_ip()

    self.response = {
      'helo':
        "HELO {}\n"
        + "IP:{}\n"
        + "Port:{}\n"
        + "StudentID:{}",
      'kill': "kill server"
    }

  def _set_ip(self):
    try:
      self.server_ip = self.get_ip_address("eth0")
    except IOError as e:
      self.server_ip = "127.0.0.1"

  def get_ip_address(self, ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
      s.fileno(),
      0x8915,  # SIOCGIFADDR
      struct.pack('256s', ifname[:15])
    )[20:24])

  def start(self):
    self.server.bind(('', self.port))
    self.server.listen(5)
    print("Running Server on PORT " + str(self.port))
    while True:
      self.__start_session()

  def __start_session(self):
    session = self.server.accept()
    user = Client(session)

    # new thread starts with function __client_handle with params user
    thread.start_new_thread(self.__client_handle, (user,))

  def __client_handle(self, client):
    self.clients.append(client)
    self.__command_handle(client)

  def __read_data(self, client):
    buff = ""
    while True:
      data = client.get_session().recv(4096)
      try:
        data = data.decode(encoding='utf-8')
      except:
        data = " "

      if not data:
        if not buff:
          break
      elif buff:
        data = buff + data
        buff = ""

      # TODO Need more work here.
      if '\r\n' in data:
        for line in data.splitlines(True):
          if line.endswith('\r\n'):
            yield line.replace("\r", "").replace("\n", "")
          else:
            buff = line
      else:
        buff += data

  def __command_handle(self, client):
    while True:
      block = None
      try:
        block = client.get_session().recv(4096)
        block = block.replace("\\n", "\n")
      except Exception as e:
        print e.args
        print e.message
        self.__client_disconnect(client)

      if block:
        cmd = [sx.split() for sx in block.encode("utf-8").split("\n") if
               len(sx) > 0]
        cmd = len(cmd) and cmd or [['']]

        print cmd
        if cmd[0][0] == "HELO":  # Helo message
          self.__helo(cmd[0][1], client)
        elif cmd[0][0] == "KILL_SERVICE":  # Kill service
          self.__kill_service()
        else:
          print("Unkown command")

  def __helo(self, text, client):
    self.__server_message(
      self.response['helo'].format(text, self.server_ip, self.port,
                                   self.student_id), client)

  def __server_message(self, msg, user=None):
    user.send(msg)

  def __kill_service(self):
    os._exit(1)

  def __client_disconnect(self, client):
    client.get_session().close()


if __name__ == "__main__":
  port = 8080
  parser = argparse.ArgumentParser(description='Argument to run server')
  parser.add_argument('--p', action="store", dest="p", type=int,
                      help='port number that socket server will run on')

  args = parser.parse_args()

  if args.p:
    port = args.p

  server = Server(port).start()
