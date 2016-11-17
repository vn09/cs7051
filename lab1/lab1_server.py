# SERVER_TEST = 'https://www.scss.tcd.ie/~ebarrett/lectures/cs4032/echo.php'

# Due to the configuration of SCSS Apache server that requires authentication
# credentials (user/password) to access, so we can't test the client code for this endpoint.
# Instead, I will write a simple server code in Python that takes parameter and reponses
# with upppercase.

from urlparse import urlparse
import
query = urlparse(self.path).query
query_components = dict(qc.split("=") for qc in query.split("&"))
imsi = query_components["imsi"]
# query_components = { "imsi" : "Hello" }

# Or use the parse_qs method
# from urlparse import urlparse, parse_qs
# query_components = parse_qs(urlparse(self.path).query)
# imsi = query_components["imsi"]

# import SimpleHTTPServer
# import SocketServer

# PORT = 8000

# Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

# httpd = SocketServer.TCPServer(("", PORT), Handler)

# print "serving at port", PORT
# httpd.serve_forever()

