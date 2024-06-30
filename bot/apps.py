from handlers.boink_app import BoinkApp
from handlers.def_app import DefApp
from handlers.tracker_app import TrackerApp


class Applications:
    PREFIX = "!"
    APPLICATIONS = {"boink": BoinkApp, "tracker": TrackerApp, "def": DefApp}
