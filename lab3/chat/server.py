#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import thread
import uuid
import re

from colorama import Fore, Style

from user import User


class Server:
  def __init__(self, port):
    self.port = port
    self.clients = list()
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.student_id = "16314667"
    self.server_ip = "127.0.0.1"
    self.chat_rooms = {}
    self.room_refs = {}

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

    # JOIN_CHATROOM: <name>\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: <client_name>
    # LEAVE_CHATROOM: <room_ref>\nJOIN_ID: <joined_id>\nCLIENT_NAME: <client_name>
    # DISCONNECT: 0\nPORT: 0\nCLIENT_NAME: <client_name>
    # CHAT: <room_ref>JOIN_ID: <joined_id>\nCLIENT_NAME: <client_id>\nMESSAGE:
    # string terminated with '\n\n'<msg>

    # Notes:
    # 1. Client can join multiple rooms and server must respone to multiple chatroom when user chats
    # 2.
    #

    self.commands = ("Protocol availables:\r\n"
                     + "/rooms                                                                     - List all rooms \r\n"
                     + "/help                                                                      - Show me this\r\n"
                     + "HELO <message>                                                             - Hello message\r\n"
                     + "KILL_SERVICE                                                               - Kill service\r\n"
                     + "JOIN_CHATROOM: <room_name> CLIENT_IP: 0 PORT: 0 CLIENT_NAME: <client_name> - Join chat room\r\n"
                     + "LEAVE_CHATROOM: <room_ref> JOIN_ID: <joined_id> CLIENT_NAME: <client_name> - Leave chat room\r\n"
                     + "DISCONNECT: 0 PORT 0 CLIENT_NAME: <client_name>                            - Disconnect client/server\r\n"
                     + "CHAT: <room_ref> JOIN_ID: <joined_id> CLIENT_NAME: <client_id> MESSAGE: <msg> - Chat in chatroom \r\n"
                     )

  def start(self):
    self.server.bind(('', self.port))
    self.server.listen(5)
    print("Running Server on PORT " + str(self.port))
    while True:
      self.__start_session()

  def __start_session(self):
    session = self.server.accept()
    user = User(session)

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
        self.__client_disconnect(client)
        break

      if block:
        if block.startswith("/help"):
          self.__server_message(self.commands, client)
        else:
          cmd = [re.split(r":|\n", sx) for sx in block.encode("utf-8").split("\n") if
                 len(sx) > 0]
          cmd = len(cmd) and cmd or [['']]
          print cmd
          if cmd[0][0] == "HELO":  # Helo message
            self.__helo(cmd[0][1], client)
          elif cmd[0][0] == "KILL_SERVICE":  # Kill service
            self.__kill_service()
          elif cmd[0][0] == "JOIN_CHATROOM" and len(cmd) == 4:  # join chat
            # TODO what is the error of joining
            room_name, client_name = cmd[0][1], cmd[3][1]
            client.set_name(client_name)
            self.__join_chat_room(room_name, client)
          elif cmd[0][0] == "LEAVE_CHATROOM" and len(cmd) == 3:
            # TODO: Multiple leave messages
            room_ref, join_id = cmd[0][1], cmd[1][1]
            self.__leave_room(room_ref, join_id, client=client)
          elif cmd[0][0] == "DISCONNECT":
            # TODO
            self.__client_disconnect(client)
          elif cmd[0][0] == "CHAT" and len(cmd) == 4:
            # TODO
            room_ref, join_id, client_name, message = [x[1] for x in cmd]
            self.__chat(room_ref, join_id, message, client)
          else:
            self.__server_message("Unknown command, try typing /help", client)

  def __list_rooms(self, client):
    for room in self.chat_rooms:
      self.__server_message(room + "(" + str(len(self.chat_rooms[room])) + ")",
                            client)

  # list users all users
  def __list_users(self, client):
    for user in self.clients:
      self.__server_message(
        "nickanme: " + str(user.get_name()) + " (" + str(user.get_room()) + ")",
        client)
    self.__server_message("Total: " + str(len(self.clients)), client)

  def __list_users_in_room(self, room, client):
    if room not in self.chat_rooms:
      self.__server_message("room doesn't exist: " + room, client)
      return
    for client_name in self.chat_rooms[room]:
      self.__server_message("nickname: " + client_name, client)
    self.__server_message("Total: " + str(len(self.chat_rooms[room])), client)

  def __send_msg_to_user(self, to_nickname, client, msg):
    if not self.__validate_msg(msg):
      return
    for user in self.clients:
      if user.get_name().lower() == to_nickname.lower():
        message = client.get_name() + " -> " + user.get_name() + ": " + msg
        self.__server_message(message, user)
        self.__server_message(message, client)
        break
      else:
        self.__server_message("User Doesn't exist", client)

  def __get_list_user_in_room(self, room):
    room_ref = self.room_refs[room]
    return [x['name'] for x in self.chat_rooms[room_ref]['clients']]

  def __send_msg_to_room(self, msg, client, res=False):
    if not self.__validate_msg(msg):
      return
    if not client.get_room():
      self.__server_message("Please join a room first.", client)
      self.__server_message("To join a room send JOIN_CHATROOM message", client)
      return

    for user in self.clients:
      if user.get_name() is not None \
              and user.get_name().lower() in self.__get_list_user_in_room(
                client.get_room()):
        response = "(" + client.get_room() + ") " + client.get_name() + ": " + msg
        if res:
          response = msg
        self.__server_message(
          response, user)

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
    if room in [client.get_room()]:
      self.__server_message("You are already in room: " + room, client)
    else:
      client.set_room(room)
      room_ref = None
      join_id = self.__generate_unique_number()

      # {'123': {'room_name': 'aa', 'clients': [{'name': 'test_1', join_id: '111'}]}}
      # Empty room
      room_names = [x['room_name'] for x in self.chat_rooms.values()]
      if room not in room_names:
        room_ref = self.__generate_unique_number()
        new_room = {'room_name': room,
                    'clients': [{'name': client.get_name().lower(),
                                 'join_id': join_id}]}
        self.chat_rooms[room_ref] = new_room
        self.room_refs[room] = room_ref
      else:  # Already had clients, just add new client
        # Get room_ref by room_name
        room_ref = self.room_refs[room]
        new_client = {'name': client.get_name().lower(),
                      'join_id': join_id}
        self.chat_rooms[room_ref]['clients'].append(new_client)

      # Respond to client
      client_res = self.response['join'].format(room, self.server_ip, self.port,
                                                room_ref, join_id)
      self.__server_message(client_res, client)

      # Broadcast msg to chatroom
      self.__send_msg_to_room("joined room", client)

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
      self.chat_rooms[room_ref]['clients'].remove(
        {'name': client.get_name().lower(), 'join_id': join_id})
    self.__send_msg_to_room("left room", client)

  def __server_message(self, msg, user=None):
    if not user:
      for client in self.clients:
        try:
          # client.send("<= " + msg)
          pass
        except:
          self.__client_disconnect(client)
    else:
      user.send(Fore.GREEN + "<= " + msg + Style.RESET_ALL)
      # user.send(msg)

  def __client_disconnect(self, client):
    client.get_session().close()
    for user in self.clients:
      if user.get_name().lower() == client.get_name().lower():
        self.clients.remove(user)

    # Remove in chat rooms
    if client.get_room():
      room_ref = self.room_refs[client.get_room()]
      self.__remove_client_name(room_ref, client.get_name().lower)

    # Send message to the chat room
    if client.get_room():
      self.__server_message(
        client.get_name() + " has left the room: " + client.get_room())
    else:
      self.__server_message(client.get_name() + " has left the chat")

  def __generate_unique_number(self):
    return int(uuid.uuid4().int >> 92)

  def __kill_service(self):
    os._exit(1)

  def __remove_client_name(self, room_ref, name):
    for (index, result) in self.chat_rooms[room_ref]['clients']:
      if result['name'] == name:
        self.chat_rooms[room_ref]['clients'].removeAtIndex(index)
        break

  def __chat(self, room_ref, join_id, msg, client):
    self.__send_msg_to_room(
      self.response['chat'].format(room_ref, client.get_name(), msg), client,
      res=True)

    # JOIN_CHATROOM: room1\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: vuong1
    # JOIN_CHATROOM: room1\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: vuong2
    # LEAVE_CHATROOM: 9733237822\nJOIN_ID: 48827036799\nCLIENT_NAME: vuong1
    #

    # Questions
    # 1. when client disconnect, do we notify to the chatroom that this client left?
    # 2. The case when multiple leave messages