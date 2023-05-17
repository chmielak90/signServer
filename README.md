# File Signing Server and Client

This project contains a server (`server.py`) and client (`client.py`) that use TLS for secure communication to sign files. The server receives a file and a signing command from a client, signs the file using `signtool.exe`, and sends it back to the client. The client then saves the signed file.

## Installation

This project has a few dependencies, which are listed in the `requirements.txt` file.

To install these dependencies, you should first make sure that you have Python installed on your system. Python 3.6 or higher is recommended.

Once Python is installed, you can install the dependencies by running the following command in your command line:

```sh
pip install -r [requirements.txt](requirements.txt)
```

This command will automatically download and install the correct versions of each dependency listed in the `requirements.txt` file.

If you're using a virtual environment (which is a good practice to isolate your project's dependencies), make sure to activate the environment before running the above command.

Please note that Markdown does not support hyperlinking for code blocks. The link to the `requirements.txt` file will not work within the code block above. However, you can refer to the file here: [requirements.txt](requirements.txt)

## Configuration

Before running the server and client scripts, you need to configure certain parameters in the `config.ini` file for the server:

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

In the `client.py` script, modify the following parameters:

- `HOST`: The IP address of the server.
- `PORT`: The port the server is listening on.
- `BUFFER_SIZE`: Buffer size in bytes used when receiving/sending data.
- Replace `"client.crt"`, `"client.key"`, and `"chain.pem"` with your client certificate, private key, and chain of trusted server certificates, respectively.

## Creating Executable Files

You can use PyInstaller to create standalone executable files from `server.py` and `client.py`. This can be useful if you want to run the server and client on machines that don't have Python installed. 

To install PyInstaller, run:

```sh
pip install pyinstaller
```

Then, to create the executable for `server.py`, run:

```sh
pyinstaller --onefile server.py
```

And for `client.py`, run:

```sh
pyinstaller --onefile client.py
```

This will create a `dist` directory containing the executables `server.exe` and `client.exe`.

## Usage

### Server

To start the server, run:

```sh
server.exe
```

The server will start listening for incoming connections. It logs all its activities, which can be viewed in the log file specified in the `config.ini` file.

### Client

To use the client, run:

```sh
client.exe <signing-command> <file-to-sign>
```

The `<signing-command>` is the command to be used by `signtool.exe` for signing, and `<file-to-sign>` is the file you want to sign.

The client sends the signing command and the file to the server, receives the signed file from the server, and saves it by overwriting the original file. If the server signs the file successfully, the client will receive an exit code of 0.

Note: The paths to the signing command and the file should be relative to the location of the `client.exe` file or absolute paths. 

The `signtool.exe` path is now configurable through `config.ini`, under the `Signtool` section. Please ensure that the path is correctly set before running the server.
## Security

The server uses certificate pinning to ensure that it only accepts connections from known clients. The certificates of allowed clients should be stored in the directory specified by the `Allowed_Clients_Dir` parameter in the `config.ini` file.

Both the server and client use TLS for secure communication, and both verify the certificate of the other party.

The client sends the file and the signing command to the server, and the server never initiates a connection to the client, which minimizes the attack surface.

## Limitations

- The server and client currently only support Windows because they rely on `signtool.exe`, which is a Windows utility.
- The server and client must have read/write access to the directories where they read/write files.
- The server does not support multiple simultaneous connections.
