import configparser
from pathlib import Path
from typing import Optional

from .profile import Profile
from ..exceptions import ProfileNotFoundException


class CartaConfig:
    carta_profiles_path = Path.home() / ".carta" / "admin_tools" / "profiles.ini"
    _config: Optional[configparser.ConfigParser]

    def __init__(self):
        self._config = None
        self.load()

    def get_profiles(self):
        return self._config.sections()

    def get_profile(self, profile: str):
        if not self._config.has_section(profile):
            raise ProfileNotFoundException()
        return Profile(**self._config[profile], profile_name=profile)

    def delete_profile(self, profile: str):
        if not self._config.has_section(profile):  # pragma: no cover
            return

        self._config.remove_section(profile)

        self.save()

    def save_profile(self, profile: str, data: Profile):
        if not self._config.has_section(profile):
            self._config.add_section(profile)
        self._config.set(profile, "username", data.username)
        self._config.set(profile, "environment", data.environment)

        # Not ideal to store pwd in plaintext, but we don't have API tokens
        if data.password:
            self._config.set(profile, "password", data.password)
        if data.token:
            self._config.set(profile, "token", data.token)

        self.save()

    def load(self):
        self._config = configparser.ConfigParser(interpolation=None)

        if not CartaConfig.carta_profiles_path.is_file():  # pragma: no cover
            # Cannot test this without breaking the global config nature of
            # the config file.
            CartaConfig.carta_profiles_path.parent.mkdir(parents=True, exist_ok=True)
            with CartaConfig.carta_profiles_path.open('x'):
                pass

        self._config.read(CartaConfig.carta_profiles_path)

        return self._config

    def save(self):
        with CartaConfig.carta_profiles_path.open('w') as config_file:
            self._config.write(config_file)
