from typing import Callable, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):

    API_KEY: Optional[str] = None
    OUTPUT_FILE_DEFAULT_NAME: Callable[[str], str] = lambda desired_format: f"synthex_output.{desired_format}"
    DEBUG_MODE: bool = False
    DEBUG_MODE_FOLDER: str = ".debug"
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="allow",
    )

    
config = Config() # type: ignore
