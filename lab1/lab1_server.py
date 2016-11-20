# SERVER_TEST = 'https://www.scss.tcd.ie/~ebarrett/lectures/cs4032/echo.php'

# Due to the configuration of SCSS Apache server that requires authentication
# credentials (user/password) to access, so we can't test the client code for this endpoint.
# Instead, I will write a simple server code in Python that takes parameter and reponses
# with upppercase.

from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import re

PORT_NUMBER = 8080

#This class will handles any incoming request from the browser
class myHandler(BaseHTTPRequestHandler):
    #Handler for the GET requests
    def do_GET(self):
        msg = "Invalid endpoint. Please use endpoint: /echo?message=xxx"
        print self.path
        if re.match(r"/echo\?message=?", self.path):
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            msg = " " + query_components["message"]
            msg = msg.upper() + "\n"

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write(msg)

        return

if __name__ == "__main__":
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print('Started httpserver on port %s' %PORT_NUMBER)

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()



