import requests
import random
import string

SERVER_TEST = "http://localhost:8000/echo/"

if __name__ == "__main__":
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])

    payload = {'message': 'test'}
    r = requests.get(SERVER_TEST, params=payload)
    print r.text