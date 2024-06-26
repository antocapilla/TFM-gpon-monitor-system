from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class MonitoringConfig(BaseModel):
    enabled: bool = True
    interval: int = 300

class MonitoringData(BaseModel):
    device_id: str = Field(..., description="Unique identifier of the device")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of the monitoring data")
    connected_hosts: Optional[int] = Field(None, description="Number of connected hosts")
    host_info: List[str] = Field(default_factory=list, description="Detailed information about each connected host")

    @validator('device_id')
    def validate_device_id(cls, v):
        if not v:
            raise ValueError('device_id cannot be empty')
        return v

    @validator('connected_hosts')
    def validate_connected_hosts(cls, v):
        if v is not None and v < 0:
            raise ValueError('connected_hosts cannot be negative')
        return v