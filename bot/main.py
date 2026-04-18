import asyncio
from .client import client
from . import handlers
from utils.logger import logger

async def main():
    await client.start()
    logger.info("welcome")
    
    await asyncio.gather(
        client.run_until_disconnected()
    )
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("stop")



