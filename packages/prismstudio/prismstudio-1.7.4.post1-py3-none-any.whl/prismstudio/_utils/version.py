import os
from typing import Literal

from .._common.config import StateSettings, ROOT_EXT_WEB_URL, URL


class Version():
    # _regex = ''
    def __init__(self) -> None:
        self._version, self._environment = self.load_setup()
        self._api_url, self._gui_url = self.load_url()

    def __repr__(self) -> str:
        return f"<Version {self.version}-{self.environment}>"

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Product Name: PrismStudio {self.version}",
                f"Version: {self.version}",
                f"Environment: {self.environment}",
                f"API_URL: {self.api_url}",
                f"GUI_URL: {self.gui_url}",
            ]
        )

    @property
    def version(self) -> str:
        return self._version

    @property
    def environment(self) -> Literal["prod", "dev", "stg"]:
        return self._environment

    @property
    def api_url(self) -> str:
        return self._api_url

    @property
    def gui_url(self) -> str:
        return self._gui_url

    def load_setup(self)-> tuple[Literal, Literal["prod", "dev", "stg"]]:
        dotenv_settings = StateSettings()
        env = os.environ.get('ENV_STATE', dotenv_settings.ENV_STATE)
        ver = dotenv_settings.VERSION
        if env == "production":
            env = 'prod'

        return ver, env

    def load_url(self):
        api = URL
        gui = ROOT_EXT_WEB_URL
        return api, gui


__version__ = str(Version())