class MockMember:
    def __init__(self, bot: bool, id: int):
        self.bot = bot or False
        self.id = id or 42


class MockGuild:
    def __init__(self):
        self.id = 1


class MockMessage:
    def __init__(self, content: str, id: int = None, bot: bool = None):
        self.content = str(content)
        self.author = MockMember(bot=bot, id=id)
        self.guild = MockGuild()
