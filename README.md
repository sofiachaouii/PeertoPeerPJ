# PeertoPeerPJ

This project implements a basic client-server architecture using Python's socket module and asyncio for asynchronous communication. The server can handle multiple client connections simultaneously and broadcast messages to all connected clients.

## Features

- Asynchronous TCP server that can handle multiple client connections
- Client implementation for connecting to the server
- Real-time message broadcasting to all connected clients
- Clean connection handling and error management

## Requirements

- Python 3.7 or higher

## Usage

1. Start the server:
```bash
python server.py
```

2. Start one or more clients in separate terminal windows:
```bash
python client.py
```

3. Once connected, clients can send messages that will be broadcast to all other connected clients.

## Implementation Details

- The server uses asyncio for asynchronous I/O operations
- Each client connection is handled in a separate task
- Messages are broadcast to all connected clients except the sender
- The server maintains a list of connected clients and their writer streams

- ChatGPT, Cursor AIs utilized to assist in this project.
