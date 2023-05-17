import configparser
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