# File Signing Server and Client

This project contains a server and a client that use TLS for secure communication to sign files (don't accept self-signed certificate). The server receives a file and a signing command from the client, signs the file using `signtool.exe`, and sends it back to the client. The client then saves the signed file.

## Requirements

- Python 3.6 or higher
- A C++ compiler if you're installing the Python requirements on Windows

## Installation

This project has a few dependencies, which are listed in the `requirements.txt` file. To install these dependencies, you should first make sure that you have Python installed on your system.

Before running the Makefile, make sure to create a Python virtual environment. This can be done as follows:

```sh
python -m venv venv
```

Then, you can use the `Makefile` to automatically build the project:

```sh
make all
```

This command will:

- Clean any previous builds.
- Install the Python dependencies in the virtual environment.
- Create version files for the client and server.
- Use PyInstaller to build standalone executables for the client and server.
- Move the executables and their dependencies to a new directory (`SignServer`).
- Compress the `SignServer` directory into a `.zip` file.

## Configuration

Before running the server and client scripts, you need to configure certain parameters in the `Server\config.ini` file for the server:

- `Server`: Contains server-specific parameters.
  - `Host`: The IP address the server will bind to.
  - `Port`: The port the server will listen on.
  - `Buffer_Size`: Buffer size in bytes used when receiving/sending data.
  - `Allowed_Clients_Dir`: Directory containing allowed clients' certificates.

- `Logging`: Contains logging-specific parameters.
  - `Filename`: The name of the file where server logs will be stored.

- `TLS`: Contains parameters for the TLS context.
  - `Certfile`: The server's certificate file.
  - `Keyfile`: The server's private key file.
  - `Chainfile`: The file with the chain of trusted client certificates.
  
- `Signtool`: Contains parameters for the signing tool.
  - `SignTool_Path`: The path to `signtool.exe`.

Before running the server and client scripts, you need to configure certain parameters in the `Client\config.ini` file for the server:

- `Server`: Contains server-specific parameters.
  - `Host`: The IP address the server will bind to.
  - `Port`: The port the server will listen on.
  - `Buffer_Size`: Buffer size in bytes used when receiving/sending data.

- `TLS`: Contains parameters for the TLS context.
  - `Certfile`: The server's certificate file.
  - `Keyfile`: The server's private key file.
  - `Chainfile`: The file with the chain of trusted client certificates.

## Usage

### Server

To start the server, run:

```sh
python server.py
```

The server will start listening for incoming connections. It logs all its activities, which can be viewed in the log file specified in the `config.ini` file.

### Client

To use the client, you need to specify the command and the file path as command line arguments. The command is the signing command that will be executed on the server. 

Run the client with the signing command and the file path:

```sh
python client.py <command> <filepath>
```

Replace `<command>` with the signing command, and `<filepath>` with the path to the file to be signed.

For example, if you're using signtool and you want to sign a file named `example.exe`, you would run:

```sh
python client.py "sign /a" example.exe
```

The client will connect to the server, send the command and the file, then wait for the server to send the signed file back. The original file will be overwritten with the signed file.

## Contributing

Contributions are welcome!

## Support

If you encounter any issues, please open an issue on our [GitHub issue tracker](https://github.com/chmielak90/signServer/issues).