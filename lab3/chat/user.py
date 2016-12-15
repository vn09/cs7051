#!/usr/bin/python
# -*- coding: utf-8 -*-

class User:
  """
  Client information. One thread can be multiple clients and join multiple chatrooms
  """

  def __init__(self, session):
    self.connection = session[0]
    self.address = session[1]
    self.list_client = []
    self.room = {}
    self.cur_name = None

  def set_name(self, client_name):
    self.cur_name = client_name
    self.list_client.append(client_name)

  def get_name(self):
    return self.cur_name

  def set_room(self, room, join_id):
    self.room[join_id] = room

  def get_room(self, join_id=None):
    if not join_id:
      return self.room.values()

    if join_id and join_id not in self.room.keys():
      return None

    return self.room[join_id]

  def send(self, msg):
    self.send_raw(str(msg) + "\n")

  def send_raw(self, msg):
    self.connection.send(str(msg).encode('utf-8'))

  def get_session(self):
    return self.connection
