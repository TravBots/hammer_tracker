import configparser
from typing import Optional
from utils.logger import logger


class ConfigService:
    _instance: Optional["ConfigService"] = None
    _config: Optional[configparser.ConfigParser] = None

    def __init__(self):
        if ConfigService._instance is not None:
            raise Exception(
                "ConfigService is a singleton class. Use ConfigService.get_instance()"
            )

        ConfigService._instance = self
        self._config = configparser.ConfigParser()
        self._reload_config()

    def get_instance() -> "ConfigService":
        if ConfigService._instance is None:
            ConfigService()
        return ConfigService._instance

    def _reload_config(self) -> None:
        """Reload the config from disk"""
        self._config.read("config.ini")

    def read_config_str(self, section: str, key: str, default: str = "") -> str:
        """Read a string value from the config"""
        try:
            return self._config[str(section)][key]
        except KeyError:
            return default

    def read_config_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Read a boolean value from the config"""
        try:
            return self._config[str(section)].getboolean(key)
        except KeyError:
            return default

    def update_config(self, section: str, key: str, value: str) -> bool:
        """Update a config value and save to disk"""
        try:
            if not self._config.has_section(str(section)):
                self._config.add_section(str(section))

            self._config[str(section)][key] = value

            with open("config.ini", "w") as conf:
                self._config.write(conf)
            return True
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False

    @property
    def config(self) -> configparser.ConfigParser:
        """Get the raw ConfigParser object"""
        return self._config


config_service = ConfigService.get_instance()


def read_config_str(section: str, key: str, default: str = "") -> str:
    return config_service.read_config_str(section, key, default)


def read_config_bool(section: str, key: str, default: bool = False) -> bool:
    return config_service.read_config_bool(section, key, default)


def update_config(section: str, key: str, value: str) -> bool:
    return config_service.update_config(section, key, value)
