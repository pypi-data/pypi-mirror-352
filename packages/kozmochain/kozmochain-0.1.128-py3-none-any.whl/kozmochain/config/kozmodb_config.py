from typing import Any, Optional

from kozmochain.config.base_config import BaseConfig
from kozmochain.helpers.json_serializable import register_deserializable


@register_deserializable
class KozmodbConfig(BaseConfig):
    def __init__(self, api_key: str, top_k: Optional[int] = 10):
        self.api_key = api_key
        self.top_k = top_k

    @staticmethod
    def from_config(config: Optional[dict[str, Any]]):
        if config is None:
            return KozmodbConfig()
        else:
            return KozmodbConfig(
                api_key=config.get("api_key", ""),
                init_config=config.get("top_k", 10),
            )
