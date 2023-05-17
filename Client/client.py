import io
import os
import socket
import ssl
import sys
import configparser

import tqdm

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'Host')  # Server IP
PORT = config.getint('Server', 'Port')  # Server port
BUFFER_SIZE = config.getint('Server', 'Buffer_Size')  # Buffer size
END_OF_FILE = b'<<EOF>>'
END_OF_RESPONSE = b'<<EOR>>'


def close_connection(conn, output, exit_code):
    # Close the connection
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

    # Print the output
    sys.stdout.write(output)
    # Exit with the same exit code as the signtool command
    sys.exit(exit_code)


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

    # Get the file size
    file_size = os.path.getsize(filepath)

    # Create a progress bar
    progress_send = tqdm(total=file_size, unit='B', unit_scale=True)

    # Send the file
    with open(filepath, 'rb') as disk_file:
        with io.BufferedReader(disk_file, buffer_size=BUFFER_SIZE) as buf_file:
            while True:
                data = buf_file.read(BUFFER_SIZE)
                if not data:
                    conn.sendall(END_OF_FILE)
                    break
                conn.sendall(data)

                # Update the progress bar
                progress_send.update(len(data))

    # Reset the progress bar for receiving the file
    progress_send.close()

    # Receive the exit code
    response_parts = []
    while True:
        data = conn.recv(BUFFER_SIZE)
        if data == END_OF_RESPONSE:
            break
        response_parts.append(data)

    response_str = b''.join(response_parts).decode('utf-8')
    output, exit_code_str = response_str.rsplit('\nExit code: ', 1)
    exit_code = int(exit_code_str)

    if exit_code != 0:
        close_connection(conn, output, exit_code)

    # Create a progress bar for receiving
    progress_get = tqdm(total=file_size, unit='B', unit_scale=True, desc='Receiving')

    # Receive the signed file and overwrite the original
    with open(filepath, 'wb') as disk_file:
        with io.BufferedWriter(disk_file, buffer_size=BUFFER_SIZE) as buf_file:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if data == END_OF_FILE:
                    break
                buf_file.write(data)

                # Update the progress bar
                progress_get.update(len(data))

    # Close the progress bar
    progress_get.close()

    # Send confirmation that the file is downloaded
    confirmation_msg = f'File {filepath} successfully downloaded.\n'
    conn.sendall(confirmation_msg.encode('utf-8'))
    conn.sendall(END_OF_RESPONSE)

    # Close the connection
    close_connection(conn, output, exit_code)
