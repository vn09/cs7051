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
    self.room = None

  def set_name(self, nick):
    self.name = nick

  def get_name(self):
    return self.name

  def set_room(self, room):
    self.room = room

  def get_room(self):
    return self.room

  def send(self, msg):
    self.send_raw(str(msg) + "\n")

  def send_raw(self, msg):
    self.connection.send(str(msg).encode('utf-8'))

  def get_session(self):
    return self.connection
