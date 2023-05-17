import socket
import ssl
import subprocess
import threading
import logging
import os

HOST = ''  # Listen on all IP addresses
PORT = 9090  # Server port
BUFFER_SIZE = 1024 * 1024 * 1024  # 1024MB
ALLOWED_CLIENTS_DIR = 'allowed_clients'  # Directory containing allowed clients' certificates
END_OF_FILE = b'<<EOF>>'

# Configure logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

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
    with open(f"temp\\{filename}", 'wb') as f:
        while True:
            data = connstream.recv(BUFFER_SIZE)
            if data == END_OF_FILE:
                break
            f.write(data)
    logging.info(f'Received file: {filename}')

    # Sign the file
    cmd = ['signtool.exe'] + signing_command + [f"temp\\{filename}"]
    result = subprocess.run(cmd, capture_output=True)

    # Log the result
    logging.info(f'Signed file: {filename}, result: {result.returncode}')

    connstream.shutdown(socket.SHUT_RDWR)
    connstream.close()

# Main function to start the server
def main():
    # Create a context for TLS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")  # Load server certificate and private key
    context.load_verify_locations(cafile="chain.pem")  #

    # Load chain of trusted client certificates
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True:
        client_conn, client_addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr, context)).start()


if __name__ == '__main__':
    main()

