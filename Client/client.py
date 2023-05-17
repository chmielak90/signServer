import configparser
import socket
import ssl

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


# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Wrap the socket with SSL
    conn = context.wrap_socket(s, server_side=False, server_hostname=HOST)

    # Connect to server
    conn.connect((HOST, PORT))

    # Close the connection
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()