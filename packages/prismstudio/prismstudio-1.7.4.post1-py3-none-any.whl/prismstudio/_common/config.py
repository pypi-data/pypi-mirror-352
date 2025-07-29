import pathlib
from enum import Enum
from pydantic_settings import BaseSettings


class EnvironmentState(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "dev"
    STAGING = "stg"
    PRODUCTION = "prod"
    DEMO = "demo"


class ModeSetting(BaseSettings):
    QUIET_MODE: bool = False

    @classmethod
    def write_mode(cls, mode):
        p = pathlib.Path(__file__).parent.resolve()
        env_file = str(p) + "/mode.env"
        with open(env_file, 'w') as f:
            f.write(f"QUIET_MODE={mode}")

    class Config:
        p = pathlib.Path(__file__).parent.resolve()
        env_file = str(p) + "/mode.env"


class StateSettings(BaseSettings):
    ENV_STATE: str = 'prod'
    VERSION: str = 'v1.7.0'
    URL_STABLE: str = 'https://api.prism39.com/v1.7'
    URL_DEV: str = 'https://ops.prism39.com'
    dev: str = ':30495'
    stg: str = ':30496'
    demo: str = ':40452'

    class Config:
        p = pathlib.Path(__file__).parent.resolve()
        env_file = str(p) + '/config.env'


class FactorySettings:
    @staticmethod
    def load():
        state = StateSettings()
        doc_url = 'help.prism39.com'
        ext_url = 'studio.prism39.com'
        if state.ENV_STATE == EnvironmentState.LOCAL:
            URL = "https://api.prism39.com/v1.7.0"
            doc_url = 'https://help.prism39.com/doc/build'
            ext_url = "https://studio.prism39.com/ext"
        elif state.ENV_STATE == EnvironmentState.DEMO:
            URL = state.URL_STABLE + getattr(state, state.ENV_STATE)
            doc_url = f"https://{state.ENV_STATE}-help.prism39.com"
            ext_url = f"https://{state.ENV_STATE}-studio.prism39.com/ext"
        elif state.ENV_STATE in (EnvironmentState.DEVELOPMENT, EnvironmentState.STAGING):
            URL = state.URL_DEV + getattr(state, state.ENV_STATE)
            doc_url = f"https://{state.ENV_STATE}-help.prism39.com"
            ext_url = f"https://{state.ENV_STATE}-studio.prism39.com/ext"
        elif state.ENV_STATE == EnvironmentState.PRODUCTION:
            URL = state.URL_STABLE
            doc_url = "https://help.prism39.com"
            ext_url = "https://studio.prism39.com/v1.7/ext"
        return URL, doc_url, ext_url


settings = FactorySettings.load()


__all__ = [
    'HEADERS',
    'URL_SERVICE',
    'URL_CATEGORYCOMPONENTS',
    'URL_DATACOMPONENTS',
    'URL_DATAQUERIES',
    'URL_TASKQUERIES',
    'URL_JOBS',
    'URL_PREFERENCES',
    'URL_PORTFOLIOS',
    'URL_UNIVERSES',
    'URL_DATAITEMS',
    'URL_FUNCTIONCOMPONENTS',
    'URL_PACKAGES',
    'URL_LOGIN',
    'URL_REFRESH',
    'URL_PASSWORD',
    'URL_UPDATE',
    'URL_STATUS',
    'URL_TASK',
    'URL_VALIDATE',
    'URL_SM',
    'URL_WEB_AUTH',
    'URL_DOC_AUTH',
    'URL_STATIC',
    'URL_DATA_FILES',
    'ROOT_EXT_WEB_URL',
    'ROOT_DOCUMENT_URL',
    'URL_UPLOAD',
    "URL_IDS",
    "ModeSetting",
]

URL, ROOT_DOCUMENT_URL, ROOT_EXT_WEB_URL = settings

HEADERS = {'Content-Type': 'application/json; charset=utf-8', 'client': 'python'}

URL_SERVICE = URL + '/service'
URL_CATEGORYCOMPONENTS = URL + '/categorycomponents'
URL_DATAQUERIES = URL + '/dataqueries'
URL_DATACOMPONENTS = URL + '/datacomponents'
URL_TASKQUERIES = URL + '/taskqueries'
URL_JOBS = URL + '/jobs'
URL_PREFERENCES = URL + '/preference'
URL_UNIVERSES = URL + '/universes'
URL_PORTFOLIOS = URL + '/portfolios'
URL_IDS = URL + "/datacategorycomponentid"
URL_DATAITEMS = URL + '/dataitems'
URL_FUNCTIONCOMPONENTS = URL + '/functioncomponents'
URL_PACKAGES = URL + '/packages'
URL_LOGIN = URL + '/auth/login'
URL_REFRESH = URL + '/refresh_token'
URL_PASSWORD = URL + '/auth/change_password'
URL_ADMIN = URL + '/admin'
URL_UPDATE = URL + '/update'
URL_STATUS = URL + '/status'
URL_TASK = URL + '/task'
URL_VALIDATE = URL + '/validate'
URL_SM = URL + '/securitymaster'
URL_WEB_AUTH = URL + '/auth/web'
URL_DOC_AUTH = URL + '/auth/doc_web'
URL_STATIC = URL + '/static'
URL_UPLOAD = URL + '/upload'
URL_DATA_FILES = URL + '/datafiles'

_username = ''
# URL = 'https://api.prism39.com'
