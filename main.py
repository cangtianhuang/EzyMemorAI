import asyncio

from services.ezymemorAI import EzyMemorAI

if __name__ == "__main__":
    ai = EzyMemorAI()
    asyncio.run(ai.run())