import io
import socket
import ssl
import subprocess
import threading
import queue
import logging
import os
import configparser

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'Host')
PORT = config.getint('Server', 'Port')  # Server port
BUFFER_SIZE = config.getint('Server', 'Buffer_Size')  # Buffer size
ALLOWED_CLIENTS_DIR = config.get('Server', 'Allowed_Clients_Dir')  # Directory containing allowed clients' certificates
END_OF_FILE = b'<<EOF>>'
END_OF_RESPONSE = b'<<EOR>>'
READY = b'>>READY>>'
SIGNTOOL_PATH = config.get('Signtool', 'SignTool_Path')  # Path to the SignTool executable

# Configure logging
logging.basicConfig(filename=config.get('Logging', 'Filename'), level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create a queue to handle signing process sequentially
signing_queue = queue.Queue()


def close_connection(connstream, filename, client_addr):
    # Remove temp files
    os.remove(f"temp\\{filename}")

    connstream.shutdown(socket.SHUT_RDWR)
    connstream.close()
    logging.info(f'Closing connection from {client_addr}')


def handle_client(conn, client_addr, context):
    logging.info(f'Got connection from {client_addr}')
    connstream = context.wrap_socket(conn, server_side=True)

    # Certificate pinning
    client_cert = connstream.getpeercert(binary_form=True)
    allowed = False
    for certfile in os.listdir(ALLOWED_CLIENTS_DIR):
        with open(os.path.join(ALLOWED_CLIENTS_DIR, certfile), 'rb') as f:
            allowed_cert_data = f.read()
        try:
            # Try to decode as PEM
            allowed_cert_pem = allowed_cert_data.decode('utf-8')
            allowed_cert_der = ssl.PEM_cert_to_DER_cert(allowed_cert_pem)
        except (UnicodeDecodeError, ValueError):
            # Not a PEM file, assume it's DER
            allowed_cert_der = allowed_cert_data
        if client_cert == allowed_cert_der:
            allowed = True
            break
    if not allowed:
        logging.info(f'Refused connection from {client_addr}: certificate not recognized')
        return

    # Receive the signing command
    data = connstream.recv(BUFFER_SIZE)
    signing_command = data.decode('utf-8').split()
    logging.info(f'Received signing command: {signing_command}')

    # Receive the filename
    data = connstream.recv(BUFFER_SIZE)
    filename = data.decode('utf-8')
    logging.info(f'Received filename data: {filename}')
    filename = os.path.basename(filename)  # Only use the basename of the filename
    logging.info(f'Using filename: {filename}')

    # Receive the file
    filename_fullpath = os.path.join('temp', filename)
    with open(filename_fullpath, 'wb') as disk_file:
        with io.BufferedWriter(disk_file, buffer_size=BUFFER_SIZE) as buf_file:
            while True:
                data = connstream.recv(BUFFER_SIZE)
                if data == END_OF_FILE:
                    break
                buf_file.write(data)
    logging.info(f'Received file: {filename}')

    # Sign the file
    cmd = [SIGNTOOL_PATH] + signing_command + [f"temp\\{filename}"]
    result = subprocess.run(cmd, capture_output=True)

    # Log the result
    logging.info(f'Signed file: {filename}, result: {result.returncode}')

    # Send the server's response
    response = result.stdout.decode() + '\nExit code: ' + str(result.returncode) + '\n'
    connstream.sendall(response.encode('utf-8'))
    connstream.sendall(END_OF_RESPONSE)

    if result.returncode != 0:
        # Close the connection
        close_connection(connstream, filename, client_addr)

    # Wait for client is ready
    while True:
        data = connstream.recv(BUFFER_SIZE)
        if data == READY:
            break
    logging.info('Client ready for receiving file')

    # Send the signed file back to the client
    filename_fullpath = os.path.join('temp', filename)
    with open(filename_fullpath, 'rb') as disk_file:
        with io.BufferedReader(disk_file, buffer_size=BUFFER_SIZE) as buf_file:
            while True:
                data = buf_file.read(BUFFER_SIZE)
                if not data:
                    connstream.sendall(END_OF_FILE)
                    break
                connstream.sendall(data)
    logging.info(f'Sent signed file: {filename}')

    # Waiting for client response - get the file
    response_parts = []
    while True:
        data = connstream.recv(BUFFER_SIZE)
        if data == END_OF_RESPONSE:
            break
        response_parts.append(data)

    response_str = b''.join(response_parts).decode('utf-8')
    logging.info(f'Client response: {response_str}')

    # Close the connection
    close_connection(connstream, filename, client_addr)


def main():
    # Create a context for TLS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=config.get('TLS', 'Certfile'), keyfile=config.get('TLS', 'Keyfile'))
    context.load_verify_locations(cafile=config.get('TLS', 'Chainfile'))

    # Load chain of trusted client certificates
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True:
        client_conn, client_addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr, context)).start()


if __name__ == '__main__':
    main()
