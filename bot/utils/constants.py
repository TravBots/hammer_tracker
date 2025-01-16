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
    HOME_QUAD = "home_quad"
    ENEMY_ALLIANCES = "enemy_alliances"
    NOTIF_CHANNEL = "notif_channel"


class Apps:
    BOINK = "boink"
    TRACKER = "tracker"
    DEF = "def"


class NotificationFlags:
    NONE = 0
    PLAYER_DELETED = 1
    ALLIANCE_CHANGE = 2
    NEW_VILLAGE = 4


APPLICATIONS = [Apps.BOINK, Apps.TRACKER, Apps.DEF]

ALLOW_FORWARDING = True
FORWARDING_MAP = {
    "1242787609365839923#1263132736558993438": "1269769409459916800#1312569623476174949",  # GWON Travco -> Gibby Scouts
    # "1147201073682055338#1147284006170267831": "1147201073682055338#1312587527231770724",  # Dev Test -> Forward Test
}

MAP_MAX = 200
MAP_MIN = -200

BOT_SERVERS_DB_PATH = "../databases/bot_servers/"
GAME_SERVERS_DB_PATH = "../databases/game_servers/"
ANALYTICS_DB_PATH = "../databases/analytics/analytics.db"

URL_PATTERN = (
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)


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
