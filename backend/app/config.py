from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    MODEL_NAME: str = "Qwen/Qwen2.5-1.5B-Instruct"
    ADAPTER_PATH: str = "app/adapters/finexplain_qwen_lora"
    ALLOW_BASE_MODEL_FALLBACK: bool = True
    MAX_CONTEXT_TOKENS: int = 1500
    TOP_K_PASSAGES: int = 3
    MAX_UPLOAD_SIZE_MB: int = 25
    DEVICE: str = "cpu"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
