class Colors:
    ERROR = 0xB22222
    SUCCESS = 0x207325
    WARNING = 0xFFFF00


class Notifications:
    NEW_VILLAGE = "new_village"

    @classmethod
    def get_values(cls):
        return [
            getattr(cls, attr) for attr in cls.__dict__ if not attr.startswith("__")
        ]


MAP_MAX = 200
MAP_MIN = -200

BOT_SERVERS_DB_PATH = "../databases/bot_servers/"
GAME_SERVERS_DB_PATH = "../databases/game_servers/"

dev_ids = [322602660555653151, 177473204011401216]

crop_production = {
    10: 280,
    11: 392,
    12: 525,
    13: 693,
    14: 889,
    15: 1120,
    16: 1400,
    17: 1820,
    18: 2240,
    19: 2800,
    20: 3430,
    21: 4270,
}
