#!/usr/bin/python
# -*- coding: utf-8 -*-

class User:
  """
  Client information. One thread can be multiple clients and join multiple chatrooms
  """

  def __init__(self, session):
    self.connection = session[0]
    self.address = session[1]
    self.name = None
    self.join_id = None
    self.room = []

  def set_name(self, client_name):
    self.name = client_name

  def get_name(self):
    return self.name

  def set_room(self, room):
    self.room.append(room)

  def get_room(self):
    return self.room

  def set_join_id(self, join_id):
    self.join_id = join_id

  def get_join_id(self):
    return self.join_id

  def send(self, msg):
    self.send_raw(str(msg) + "\n")

  def send_raw(self, msg):
    self.connection.send(str(msg).encode('utf-8'))

  def get_session(self):
    return self.connection
