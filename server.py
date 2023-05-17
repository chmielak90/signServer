import logging
import socket

HOST = ''  # Listen on all available interfaces
PORT = 9090
BUFFER_SIZE = 1024 * 1024 * 1024

# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def handle_client(client_socket):
    # Receive data from the client
    data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
    print(f"Received data from client: {data}")

    # Send a response back to the client
    response = "Hello, client! I received your message."
    client_socket.sendall(response.encode('utf-8'))

    # Close the client socket
    client_socket.close()

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow reuse of the address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to a specific address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}")

while True:
    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connected to client: {client_address[0]}:{client_address[1]}")

    # Handle the client connection in a separate thread
    handle_client(client_socket)
