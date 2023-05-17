import logging

HOST = ''  # Listen on all IP addresses
PORT = 9090  # Server port
BUFFER_SIZE = 1024 * 1024 * 1024  # 1024MB


# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

