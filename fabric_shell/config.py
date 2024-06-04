from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_core import ValidationError


class ClockModel(BaseModel):
    time: str = Field(default="%X")
    date: str = Field(default="%x")


class LoggingModel(BaseModel):
    level: Literal[
        "CRITICAL",
        "ERROR",
        "WARNING",
        "SUCCESS",
        "INFO",
        "DEBUG",
        "TRACE",
    ] = Field(default="INFO")


class ConfigModel(BaseModel):
    # TODO test for None values etc
    # TODO validate default values (fool proof if we pass some shit as default value)
    clock: ClockModel = Field(default_factory=ClockModel)
    logging: LoggingModel = Field(default_factory=LoggingModel)


def load_config():
    try:
        # TODO what if file don't exist?
        yaml_data = Path("config.yaml").read_text()
        config_data = yaml.safe_load(yaml_data) or dict()
        return ConfigModel(**config_data)

    except ValidationError as e:
        print(e)
        exit()


config = load_config()
