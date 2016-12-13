import requests
import random
import socket
import string

PORT_NUMBER = 8080
HOST_DOMAIN = ""

if __name__ == "__main__":
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST_DOMAIN, PORT_NUMBER))
  try:
    random_string = ''.join(random.choice(string.digits + string.ascii_lowercase) for x in range(10))
    msgs = ['KILL_SERVICE\n', 'HELO ' + random_string + '\n']
    msg = random.choice(msgs)
    sock.sendall(msg)
    response = sock.recv(1024)
    print(response)
  finally:
    sock.close()
