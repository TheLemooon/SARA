import http.server
import socketserver
import os

# Set the port number
PORT = 8000
HOST = '10.42.0.2'

# Change directory to the current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Define the handler to serve files
Handler = http.server.SimpleHTTPRequestHandler

# Create a TCP socket server
with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    # Start the server
    httpd.serve_forever()
