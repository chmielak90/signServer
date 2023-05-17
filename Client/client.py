import socket
import ssl
import sys
import configparser

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('Server', 'Host')  # Server IP
PORT = config.getint('Server', 'Port')  # Server port
BUFFER_SIZE = config.getint('Server', 'Buffer_Size')  # Buffer size
END_OF_FILE = b'<<EOF>>'

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

    # Send the file
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                conn.sendall(END_OF_FILE)
                break
            conn.sendall(data)

    # Receive the signed file and overwrite the original
    with open(filepath, 'wb') as f:
        while True:
            data = conn.recv(BUFFER_SIZE)
            if data == END_OF_FILE:
                break
            f.write(data)

    # Send confirmation that the file is downloaded
    confirmation_msg = f'File {filepath} successfully downloaded.\n'
    conn.sendall(confirmation_msg.encode('utf-8'))
    conn.sendall(END_OF_FILE)

    # Receive the exit code
    response_parts = []
    while True:
        data = conn.recv(BUFFER_SIZE)
        if data == END_OF_FILE:
            break
        response_parts.append(data)

    response_str = b''.join(response_parts).decode('utf-8')
    output, exit_code_str = response_str.rsplit('\nExit code: ', 1)
    exit_code = int(exit_code_str)

    # Close the connection
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

    # Print the output
    sys.stdout.write(output)
    # Exit with the same exit code as the signtool command
    sys.exit(exit_code)
