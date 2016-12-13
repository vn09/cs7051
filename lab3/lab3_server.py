#!/usr/bin/python
# -*- coding: utf-8 -*-

from chat.server import Server
import argparse

if __name__ == '__main__':
  port = 8080
  parser = argparse.ArgumentParser(description='Argument to run server')
  parser.add_argument('--p', action="store", dest="p", type=int,
                      help='port number that socket server will run on')

  args = parser.parse_args()

  if args.p:
    port = args.p

  server = Server(port).start()
