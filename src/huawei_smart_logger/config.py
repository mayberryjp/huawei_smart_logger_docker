from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    huawei_host: str = "https://192.168.50.38"
    huawei_username: str = "admin"
    huawei_password: str = ""
    mqtt_host: str = "earthquake.832-5.jp"
    mqtt_port: int = 1883
    mqtt_username: str = "japan"
    mqtt_password: str = ""
    sleep_interval: int = 60


settings = Settings()