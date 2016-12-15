#!/usr/bin/python
# -*- coding: utf-8 -*-

class User:
  """
  Client information
  """

  def __init__(self, session):
    self.connection = session[0]
    self.address = session[1]
    self.name = None
    self.room = {}

  def set_name(self, client_name):
    self.name = client_name

  def get_name(self):
    return self.name

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
