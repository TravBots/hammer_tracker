class Colors:
    ERROR = 0xB22222
    SUCCESS = 0x207325
    WARNING = 0xFFFF00


class ConfigKeys:
    TOKEN = "token"
    GAME_SERVER = "game_server"
    SERVER = "server"
    DATABASE = "database"
    INIT_USER = "init_user"
    ADMIN_ROLE = "admin_role"
    USER_ROLE = "user_role"
    ANVIL_ROLE = "anvil_role"
    DEFENSE_CHANNEL = "defense_channel"
    ALERTS = "alerts"
    IGNORE_24_7 = "ignore_24_7"
    CLEAN_UP_THREADS = "clean_up_threads"
    DEFAULT = "default"


class Apps:
    BOINK = "boink"
    TRACKER = "tracker"
    DEF = "def"


APPLICATIONS = [Apps.BOINK, Apps.TRACKER, Apps.DEF]

MAP_MAX = 200
MAP_MIN = -200

BOT_SERVERS_DB_PATH = "../databases/bot_servers/"
GAME_SERVERS_DB_PATH = "../databases/game_servers/"

pytest_id = 1234
ci_cd_id = 1312198246059348030
dev_ids = [322602660555653151, 177473204011401216, ci_cd_id]


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
