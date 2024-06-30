from handlers.boink_app import BoinkApp
from handlers.tracker_app import TrackerApp
from handlers.def_app import DefApp
from handlers.notification_app import NotificationApp


class Applications:
    PREFIX = "!"
    APPLICATIONS = {
        "boink": BoinkApp,
        "tracker": TrackerApp,
        "def": DefApp,
        "notif": NotificationApp,
    }
