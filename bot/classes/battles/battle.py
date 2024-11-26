from bot.objects.base_module import BaseModule
from bot.classes.battles.dungeon import Dungeon


class Battle(BaseModule):
    dungeon: Dungeon

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dungeon = Dungeon(self)

    async def hello(self, event):
        print("hello from battle-go()")