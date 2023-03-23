import asyncio
from bot.classes.TgClass import TgClass


async def main():
    tb = TgClass()
    print(
        tb.admins
    )

asyncio.run(main())
