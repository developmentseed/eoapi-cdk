from typing import Dict

import pydantic
import yaml
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env"
    )
    aws_default_account: str = pydantic.Field(
        description="AWS account ID"
    )
    project_id: str = pydantic.Field(
        description="Project ID", default="eoapi-cdk-integration"
    )
    stage: str = pydantic.Field(description="Stage of deployment", default="test")
    # because of its validator, `tags` should always come after `project_id` and `stage`
    tags: Dict[str, str] | None = pydantic.Field(
        description="""Tags to apply to resources. If none provided,
        will default to the defaults defined in `default_tags`.
        Note that if tags are passed to the CDK CLI via `--tags`,
        they will override any tags defined here.""",
        default=None,
    )
    db_instance_type: str = pydantic.Field(
        description="Database instance type", default="t3.micro"
    )
    db_allocated_storage: int = pydantic.Field(
        description="Allocated storage for the database", default=5
    )

    @pydantic.field_validator("tags")
    def default_tags(cls, v, info: FieldValidationInfo):
        return v or {"project_id": info.data["project_id"], "stage": info.data["stage"]}

    def build_service_name(self, service_id: str) -> str:
        return f"{self.project_id}-{self.stage}-{service_id}"


def build_app_config() -> AppConfig:
    """Builds the AppConfig object from config.yaml file if exists,
    otherwise use defaults"""
    try:
        with open("config.yaml") as f:
            print("Loading config from config.yaml")
            app_config = yaml.safe_load(f)
            app_config = (
                {} if app_config is None else app_config
            )  # if config is empty, set it to an empty dict
            app_config = AppConfig(**app_config)
    except FileNotFoundError:
        # if no config at the expected path, using defaults
        app_config = AppConfig()

    return app_config
