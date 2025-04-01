import asyncio
import logging
from typing import Dict, Set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.clients: Dict[asyncio.StreamWriter, str] = {}
        self.server = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connections."""
        client_id = id(writer)
        self.clients[writer] = f"Client-{client_id}"
        
        try:
            # send welcome message
            writer.write(f"Welcome {self.clients[writer]}!\n".encode())
            await writer.drain()
            
            # broadcast new client connection
            await self.broadcast(f"{self.clients[writer]} has joined the chat.\n", exclude=writer)
            
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                    
                message = data.decode().strip()
                if message:
                    await self.broadcast(f"{self.clients[writer]}: {message}\n", exclude=writer)
                    
        except Exception as e:
            logger.error(f"Error handling client {self.clients[writer]}: {e}")
        finally:
            # clean up connection
            await self.disconnect_client(writer)

    async def broadcast(self, message: str, exclude: asyncio.StreamWriter = None):
        """Broadcast message to all connected clients except the excluded one."""
        for writer in self.clients:
            if writer != exclude:
                try:
                    writer.write(message.encode())
                    await writer.drain()
                except Exception as e:
                    logger.error(f"Error broadcasting to {self.clients[writer]}: {e}")
                    await self.disconnect_client(writer)

    async def disconnect_client(self, writer: asyncio.StreamWriter):
        """Handle client disconnection."""
        if writer in self.clients:
            client_name = self.clients[writer]
            writer.close()
            await writer.wait_closed()
            del self.clients[writer]
            await self.broadcast(f"{client_name} has left the chat.\n")

    async def start(self):
        """Start the chat server."""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )
            logger.info(f"Server started on {self.host}:{self.port}")
            
            async with self.server:
                await self.server.serve_forever()
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.server.close()
            await self.server.wait_closed()

async def main():
    server = ChatServer()
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user") 