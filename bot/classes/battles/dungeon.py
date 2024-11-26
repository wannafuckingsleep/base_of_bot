from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.classes.battles.battle import Battle

class Dungeon:
    def __init__(self, battle: "Battle"):
        self.battle = battle

    async def hello(self, event):
        await self.battle.bot.hello(event)
        await self.battle.hello(event)
        print("hello from battle-dungeon-go()")