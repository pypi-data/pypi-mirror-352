from pydantic_settings import BaseSettings


class EntraWebhookSettings(BaseSettings):
    pubsub_topic_path: str
    expected_service_principal_guid: str

    class Config:
        env_prefix = "ENTRA_"


settings = EntraWebhookSettings()  # type: ignore[call-arg]
