from typing import Dict

import structlog
from pydantic import BaseModel, Field

from ..models.arrow import ArrowStreamConfig

logger = structlog.get_logger()


class StreamConfig(BaseModel):
    """Root configuration for all streams."""

    streams: dict[str, ArrowStreamConfig] = Field(
        default_factory=dict, description="Stream configurations keyed by stream name"
    )


class StreamConfigManager:
    """Stream configuration manager."""

    def __init__(self) -> None:
        """Initialize the stream configuration manager."""
        self._configs: Dict[str, StreamConfig] = {}

    def get_config(self, stream_name: str) -> StreamConfig:
        """Get stream configuration."""
        if stream_name not in self._configs:
            # Create default config
            self._configs[stream_name] = StreamConfig(
                target_table=stream_name,
            )
        return self._configs[stream_name]

    def set_config(self, stream_name: str, config: StreamConfig) -> None:
        """Set stream configuration."""
        self._configs[stream_name] = config


# Create global stream config manager instance
stream_config_manager = StreamConfigManager()
