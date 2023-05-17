import configparser
import socket
import ssl
import sys

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'Host')  # Server IP
PORT = config.getint('Server', 'Port')  # Server port
BUFFER_SIZE = config.getint('Server', 'Buffer_Size')  # Buffer size

# Create an SSL context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_cert_chain(certfile=config.get('Client', 'Certfile'), keyfile=config.get('Client', 'Keyfile'))
context.load_verify_locations(cafile=config.get('Client', 'Chainfile'))

# Get the command and the file path from command line arguments
command = ' '.join(sys.argv[1:-1])
filepath = sys.argv[-1]

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Wrap the socket with SSL
    conn = context.wrap_socket(s, server_side=False, server_hostname=HOST)

    # Connect to server
    conn.connect((HOST, PORT))

    # Send the command
    conn.sendall(command.encode())

    # Send the filename
    conn.sendall(filepath.encode())

    # Close the connection
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()