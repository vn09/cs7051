#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import thread
import uuid
import re
import fcntl
import struct

from user import User


class Server:
  def __init__(self, port):
    self.port = port
    self.clients = list()
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.student_id = "16314667"
    self.chat_rooms = {}
    self.room_refs = {}

    self._set_ip()

    self.response = {
      'helo':
        "HELO {}\n"
        + "IP:{}\n"
        + "Port:{}\n"
        + "StudentID:{}",
      'kill': "kill server",
      'join':
        "JOINED_CHATROOM: {}\n"
        + "SERVER_IP: {}\n"
        + "PORT: {}\n"
        + "ROOM_REF: {}\n"
        + "JOIN_ID: {}"
      ,
      'leave':
        "LEFT_CHATROOM: {}\n"
        + "JOIN_ID: {}"
      ,
      'disconnect':
        'terminate server/client connection'
      ,
      'chat':
        "CHAT: {}\n"
        "CLIENT_NAME: {}\n"
        "MESSAGE: {}\n"
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
    user = User(session)

    # Initialise join id
    join_id = str(self.__generate_unique_number())
    user.set_join_id(join_id)

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
    """
    :type client: object
    """
    while True:
      block = None
      try:
        block = client.get_session().recv(4096)
        block = block.replace("\\n", "\n")
      except Exception as e:
        client.get_session().close()
        break

      if block:
        cmd = []
        for sx in block.encode("utf-8").split("\n"):
          if len(sx) > 0:
            sub_cmd = re.split(r"\r| |:|\n", sx)
            sub_cmd = [x for x in sub_cmd if len(x) > 0]
            if len(sub_cmd) > 0:
              cmd.append(sub_cmd)

        if cmd[0][0] == "HELO":  # Helo message
          self.__helo(cmd[0][1], client)
        elif cmd[0][0] == "KILL_SERVICE":  # Kill service
          self.__kill_service()
        elif cmd[0][0] == "JOIN_CHATROOM" and len(cmd) == 4:  # join chat
          room_name, client_name = cmd[0][1], cmd[3][1]

          client.set_name(client_name)
          client.set_room(room_name)

          self.__join_chat_room(room_name, client)
        elif cmd[0][0] == "LEAVE_CHATROOM" and len(cmd) == 3:
          room_ref, join_id = cmd[0][1], cmd[1][1]
          self.__leave_room(room_ref, join_id, client=client)
        elif cmd[0][0] == "DISCONNECT":
          self.__client_disconnect(client)
        elif cmd[0][0] == "CHAT" and len(cmd) == 4:
          room_ref, join_id, client_name = [cmd[id][1] for id in range(3)]
          message = " ".join(cmd[3][1:])
          self.__chat(room_ref, message, client)
        else:
          print("Unknown command.")

  def __get_list_user_in_room(self, room_ref):
    return [x['name'] for x in self.chat_rooms[room_ref]['clients']]

  def __send_msg_to_room(self, msg, client, room_ref):
    if not self.__validate_msg(msg):
      return

    if not client.get_room():
      self.__server_message("Please join a room first.", client)
      self.__server_message("To join a room send JOIN_CHATROOM message", client)
      return

    for user in self.clients:
      if user.get_name() is not None \
              and user.get_name().lower() in self.__get_list_user_in_room(
                room_ref):
        self.__server_message(msg, user)

  def __validate_msg(self, msg):
    return msg != ""

  def __join_chat_room(self, room, client):
    """
    Join current client to given room. It also notifies other client in the room
    Note that, client maybe joins multiple rooms

    :param room: room name
    :param client: the client that connects to server currently
    :return:
    """

    room_ref = None
    room_names = [x['room_name'] for x in self.chat_rooms.values()]
    if room not in room_names:
      room_ref = str(self.__generate_unique_number())
      new_room = {'room_name': room,
                  'clients': [{'name': client.get_name().lower(),
                               'join_id': client.get_join_id()}]}
      self.chat_rooms[room_ref] = new_room
      self.room_refs[room] = room_ref
    else:  # Already had clients, just add new client
      # Get room_ref by room_name
      room_ref = self.room_refs[room]
      new_client = {'name': client.get_name().lower(),
                    'join_id': client.get_join_id()}
      self.chat_rooms[room_ref]['clients'].append(new_client)

    # Respond to client
    client_res = self.response['join'].format(room, self.server_ip, self.port,
                                              room_ref, client.get_join_id())
    self.__server_message(client_res, client)

    # Broadcast msg to chatroom
    msg = self.response['chat'].format(room_ref, client.get_name(),
                                       "{} has joined this chatroom.".format(
                                         client.get_name()))
    self.__send_msg_to_room(msg, client, room_ref)

  def __helo(self, text, client):
    self.__server_message(
      self.response['helo'].format(text, self.server_ip, self.port,
                                   self.student_id), client)

  def __leave_room(self, room_ref, join_id, client):
    # Send response message for current client
    self.__server_message(self.response['leave'].format(room_ref, join_id),
                          client)

    # Broadcast message to other clients in chatroom
    if room_ref in self.chat_rooms.keys():
      msg = self.response['chat'].format(room_ref, client.get_name(),
                                         "{} has left this chatroom.".format(
                                           client.get_name()))
      self.__send_msg_to_room(msg, client, room_ref)

      # remove chat room
      if {'name': client.get_name().lower(), 'join_id': join_id} in \
              self.chat_rooms[room_ref]['clients']:
        self.chat_rooms[room_ref]['clients'].remove(
          {'name': client.get_name().lower(), 'join_id': join_id})

    # Remove room in client
    room_name = self.chat_rooms[room_ref]["room_name"]
    client.remove_room(room_name)

  def __server_message(self, msg, user=None):
    if not user:
      for client in self.clients:
        try:
          pass
        except:
          self.__client_disconnect(client)
    else:
      user.send(msg)

  def __client_disconnect(self, client):
    # Broadcast chat message
    if client.get_room():
      for room in client.get_room():
        room_ref = self.room_refs[room]
        self.__chat(room_ref,
                    '{} has left this chatroom.'.format(client.get_name()),
                    client)
    else:
      self.__server_message(client.get_name() + " has left the chat")

    # Remove client from chatroom
    if client.get_room():
      for room in client.get_room():
        room_ref = self.room_refs[room]
        if client.get_name():
          self.__remove_client_name(room_ref, client.get_name().lower())

    for user in self.clients:
      if user.get_name() and user.get_name().lower() == client.get_name().lower():
        self.clients.remove(user)
    client.get_session().close()

  def __generate_unique_number(self):
    return int(uuid.uuid4().int >> 92)

  def __kill_service(self):
    os._exit(1)
    for user in self.clients:
      user.get_session().shutdown(socket.SHUT_RDWR)
      user.get_session().close()

    self.server.shutdown(socket.SHUT_RDWR)
    self.server.close()

  def __remove_client_name(self, room_ref, name):
    for (index, result) in enumerate(self.chat_rooms[room_ref]['clients']):
      if result['name'] == name:
        del (self.chat_rooms[room_ref]['clients'][index])
        break

  def __chat(self, room_ref, msg, client):
    # When one client chat to the chatroom, all clients in the chatroom
    # should receive the message.
    self.__send_msg_to_room(
      self.response['chat'].format(room_ref, client.get_name(), msg), client,
      room_ref)
