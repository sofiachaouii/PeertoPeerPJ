import asyncio
import logging
import sys
from typing import Optional

# configure 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatClient:
    def __init__(self, host: str = '127.0.0.1', port: int = 8888):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def connect(self):
        """Connect to the chat server."""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host,
                self.port
            )
            logger.info(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            sys.exit(1)

    async def receive_messages(self):
        """Receive and display messages from the server."""
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    break
                message = data.decode()
                print(message, end='')
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
        finally:
            await self.disconnect()

    async def send_messages(self):
        """Send messages to the server."""
        try:
            while True:
                message = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )
                if message.lower() == 'quit':
                    break
                self.writer.write(message.encode() + b'\n')
                await self.writer.drain()
        except Exception as e:
            logger.error(f"Error sending messages: {e}")
        finally:
            await self.disconnect()

    async def disconnect(self):
        """Disconnect from the server."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info("Disconnected from server")

    async def start(self):
        """Start the chat client."""
        await self.connect()
        
        # create tasks to send/receive messages
        receive_task = asyncio.create_task(self.receive_messages())
        send_task = asyncio.create_task(self.send_messages())
        
        # wait for a task to complete
        done, pending = await asyncio.wait(
            [receive_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # cancel pending tasks
        for task in pending:
            task.cancel()
        
        # wait for tasks to complete
        await asyncio.gather(*pending, return_exceptions=True)

async def main():
    client = ChatClient()
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client stopped by user") 