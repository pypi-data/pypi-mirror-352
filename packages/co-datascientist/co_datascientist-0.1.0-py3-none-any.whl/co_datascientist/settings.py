import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import keyring

load_dotenv()
KEYRING_USERNAME = "user"

class Settings(BaseSettings):
    service_name: str = "CoDatascientist"
    api_key: SecretStr = ""
    log_level: int = logging.ERROR
    host: str = "localhost"
    port: int = 8000
    wait_time_between_checks_seconds: int = 10
    co_datascientist_backend_url: str = "http://localhost:8001"

    def get_api_key(self):
        token = keyring.get_password(self.service_name, KEYRING_USERNAME)
        if not token:
            token = input("paste your api key: ").strip()
            keyring.set_password(self.service_name, KEYRING_USERNAME, token)
        self.api_key = SecretStr(token)

    def delete_api_key(self):
        keyring.delete_password(self.service_name, KEYRING_USERNAME)

settings = Settings()
