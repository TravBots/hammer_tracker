class Colors:
    ERROR = 0xB22222
    SUCCESS = 0x207325
    WARNING = 0xFFFF00

class Config:
    DATABASE = "database"
    ADMIN_ROLE = "admin_role"
    USER_ROLE = "user_role"
    ANVIL_ROLE = "anvil_role"
    ID = "id"

##### COMMANDS #####

COMMAND_PREFIX = "!"

class Commands:

    class Tracker:
        INIT = COMMAND_PREFIX + "tracker init"
        SET_ADMIN = COMMAND_PREFIX + "tracker set admin"
        SET_USER = COMMAND_PREFIX + "tracker set user"
        SET_SERVER = COMMAND_PREFIX + "tracker set server"
        INFO = COMMAND_PREFIX + "tracker info"
        ADD = COMMAND_PREFIX + "tracker add"
        GET = COMMAND_PREFIX + "tracker get"
        DELETE = COMMAND_PREFIX + "tracker delete"
        LIST_ALL = COMMAND_PREFIX + "tracker list all"
        HELP = COMMAND_PREFIX + "tracker"

    class General:
        DEV_INFO = COMMAND_PREFIX + "dev info"
        GEAR = COMMAND_PREFIX + "gear"

    class Defense:
        SET_ANVIL_ROLE = COMMAND_PREFIX + "def set anvil role"
        SET_CHANNEL = COMMAND_PREFIX + "def set channel"
        LIST_OPEN = COMMAND_PREFIX + "def list open"
        SEND = COMMAND_PREFIX + "def send"
        LEADERBOARD = COMMAND_PREFIX + "def leaderboard"
        
