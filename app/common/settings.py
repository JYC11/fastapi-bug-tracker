import enum
import os
import sys

from pydantic import BaseSettings, SecretStr


class StageEnum(str, enum.Enum):
    TEST = "testing"
    LOCAL = "local"
    DEV = "development"
    STAGE = "staging"
    PROD = "production"


# TODO: add thing to get secret variables when stage is not in testing, local

if "pytest" in sys.modules:
    os.environ["STAGE"] = StageEnum.TEST.value

if not os.getenv("STAGE"):
    raise Exception("STAGE is not defined")


class DBSettings(BaseSettings):
    server: str = "localhost"
    user: str = "jason"
    password: SecretStr = SecretStr("")
    db: str = "bug_tracker"
    port: int = 5432
    pool_size: int = 10
    max_overflow: int = 10

    @property
    def url(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.user, self.password.get_secret_value(), self.server, self.port, self.db
        )

    @property
    def test_db(self) -> str:
        return f"{self.db}_test"

    @property
    def test_url(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.user, self.password.get_secret_value(), self.server, self.port, self.test_db
        )

    class Config:
        env_prefix = "postgres_"
        env_file = ".env"


db_settings = DBSettings()


class Settings(BaseSettings):
    stage: StageEnum = StageEnum.LOCAL
    working_on_pipeline: bool = False
    service_name: str = "recipe"
    tz: str = "Asia/Seoul"

    api_v1_str: str = "/api/v1"
    backoffice_prefix: str = "/backoffice"
    enduser_prefix: str = "/enduser"
    internal_prefix: str = "/internal"
    external_prefix: str = "/external"

    backend_cors_origins: list[str] = ["*"]

    db_settings: DBSettings = db_settings

    class Config:
        env_file = ".env"


settings = Settings()
