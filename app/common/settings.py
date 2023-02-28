import enum
import os
import sys
from base64 import b64encode
from datetime import timedelta

from pydantic import BaseSettings, Field, SecretStr


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
            self.user,
            self.password.get_secret_value(),
            self.server,
            self.port,
            self.test_db,
        )

    class Config:
        env_prefix = "postgres_"
        env_file = ".env"


class JWTSettings(BaseSettings):
    raw_secret: SecretStr = Field(..., env="SECRET_KEY")
    public_key: str | None = None
    private_key: str | None = None
    algorithm: str = "HS256"
    authorization_type: str = "Bearer"
    verify: bool = True
    verify_expiration: bool = True
    expiration_delta = timedelta(minutes=30)
    refresh_expiration_delta = timedelta(days=15)
    allow_refresh = True
    access_toke_expire_minutes = 60 * 24 * 8

    @property
    def secret_key(self):
        return SecretStr(b64encode(self.raw_secret.get_secret_value().encode()).decode())


db_settings = DBSettings()
jwt_settings = JWTSettings()


class Settings(BaseSettings):
    stage: StageEnum = StageEnum.LOCAL
    working_on_pipeline: bool = False
    service_name: str = "recipe"
    tz: str = "Asia/Seoul"

    api_v1_str: str = "/api/v1"
    api_v1_login_url: str = "/api/v1/external/enduser/login"
    backoffice_prefix: str = "/backoffice"
    enduser_prefix: str = "/enduser"
    internal_prefix: str = "/internal"
    external_prefix: str = "/external"
    test_url: str = "http://test"

    backend_cors_origins: list[str] = ["*"]

    db_settings: DBSettings = db_settings
    jwt_settings: JWTSettings = jwt_settings

    class Config:
        env_file = ".env"


settings = Settings()
