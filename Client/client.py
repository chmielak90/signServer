import io
import os
import socket
import ssl
import sys
import configparser

from tqdm import tqdm

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'Host')  # Server IP
PORT = config.getint('Server', 'Port')  # Server port
BUFFER_SIZE = config.getint('Server', 'Buffer_Size')  # Buffer size
END_OF_FILE = b'<<EOF>>'
END_OF_RESPONSE = b'<<EOR>>'
READY = b'>>READY>>'
PROGRESS_BUFFER_SIZE = 1024


def close_connection(connstream, output, exit_code):
    # Close the connection
    connstream.shutdown(socket.SHUT_RDWR)
    connstream.close()

    # Print the output
    sys.stdout.write(output)
    # Exit with the same exit code as the signtool command
    sys.exit(exit_code)


# Create an SSL context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_cert_chain(certfile=config.get('TLS', 'Certfile'), keyfile=config.get('Client', 'Keyfile'))
context.load_verify_locations(cafile=config.get('TLS', 'Chainfile'))

# Get the command and the file path from command line arguments
command = ' '.join(sys.argv[1:-1])
filepath = sys.argv[-1]

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    # Wrap the socket with SSL
    connstream= context.wrap_socket(s, server_side=False, server_hostname=HOST)

    # Connect to server
    connstream.connect((HOST, PORT))

    # Send the command
    connstream.sendall(command.encode())

    # Send the filename
    connstream.sendall(filepath.encode())

    # Get the file size
    file_size = os.path.getsize(filepath)

    # Create a progress bar for sending
    progress_send = tqdm(total=file_size, unit='B', unit_scale=True, desc='Sending')

    # Read the file with a large buffer and send it with a smaller one
    with open(filepath, 'rb') as disk_file:
        with io.BufferedReader(disk_file, buffer_size=BUFFER_SIZE) as buf_file:
            while True:
                buffer = buf_file.read(BUFFER_SIZE)
                if not buffer:
                    connstream.sendall(END_OF_FILE)
                    break
                for i in range(0, len(buffer), PROGRESS_BUFFER_SIZE):
                    segment = buffer[i:i + PROGRESS_BUFFER_SIZE]
                    connstream.sendall(segment)

                    # Update the progress bar
                    progress_send.update(len(segment))

    # Close the progress bar after sending
    progress_send.close()

    # Receive the exit code
    response_parts = []
    while True:
        data = connstream.recv(BUFFER_SIZE)
        if data == END_OF_RESPONSE:
            break
        response_parts.append(data)

    response_str = b''.join(response_parts).decode('utf-8')
    output, exit_code_str = response_str.rsplit('\nExit code: ', 1)
    exit_code = int(exit_code_str)

    if exit_code != 0:
        close_connection(connstream, output, exit_code)
    # Ready for file receiving
    connstream.sendall(READY)

    # Create a progress bar for receiving
    progress_get = tqdm(total=file_size, unit='B', unit_scale=True, desc='Receiving')

    # Create a progress bar for receiving
    progress_get = tqdm(total=file_size, unit='B', unit_scale=True, desc='Receiving')

    # Receive the signed file and overwrite the original
    with open(filepath, 'wb') as disk_file:
        while True:
            buffer = connstream.recv(BUFFER_SIZE)
            if not buffer or buffer == END_OF_FILE:
                break
            disk_file.write(buffer)

            # Update the progress bar
            progress_get.update(len(buffer))

    # Close the progress bar
    progress_get.close()

    # Send confirmation that the file is downloaded
    confirmation_msg = f'File {filepath} successfully downloaded.\n'
    connstream.sendall(confirmation_msg.encode('utf-8'))
    connstream.sendall(END_OF_RESPONSE)

    # Close the connection
    close_connection(connstream, output, exit_code)
