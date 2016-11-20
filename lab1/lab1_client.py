import requests
import random
import string

PORT_NUMBER = 8080
HOST_DOMAIN = "http://localhost"
TEST_ENDPOINT = HOST_DOMAIN + ":" + str(PORT_NUMBER) + "/echo"

if __name__ == "__main__":
    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])

    payload = {'message': random_string}
    r = requests.get(TEST_ENDPOINT, params=payload)
    print r.text
