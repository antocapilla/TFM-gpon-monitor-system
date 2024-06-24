from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class MonitoringConfig(BaseModel):
    enabled: bool = True
    interval: int = 300

class HostInfo(BaseModel):
    ip_address: Optional[str] = Field(None, description="IP address of the connected host")
    address_source: Optional[str] = Field(None, description="Source of the IP address (e.g., DHCP, static)")
    lease_time_remaining: Optional[int] = Field(None, description="Remaining lease time for DHCP-assigned IP address")
    mac_address: Optional[str] = Field(None, description="MAC address of the connected host")
    host_name: Optional[str] = Field(None, description="Host name of the connected device")
    interface_type: Optional[str] = Field(None, description="Type of interface (e.g., Ethernet, WiFi)")
    active: Optional[bool] = Field(None, description="Indicates if the host is currently active")

class EthernetStats(BaseModel):
    bytes_received: Optional[int] = Field(None, description="Total bytes received on the Ethernet interface")
    bytes_sent: Optional[int] = Field(None, description="Total bytes sent on the Ethernet interface")
    packets_received: Optional[int] = Field(None, description="Total packets received on the Ethernet interface")
    packets_sent: Optional[int] = Field(None, description="Total packets sent on the Ethernet interface")

class WiFiStats(BaseModel):
    total_bytes_received: Optional[int] = Field(None, description="Total bytes received on the WiFi interface")
    total_bytes_sent: Optional[int] = Field(None, description="Total bytes sent on the WiFi interface")
    total_packets_received: Optional[int] = Field(None, description="Total packets received on the WiFi interface")
    total_packets_sent: Optional[int] = Field(None, description="Total packets sent on the WiFi interface")

class MonitoringData(BaseModel):
    device_id: str = Field(..., description="Unique identifier of the device")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp of the monitoring data")
    connected_hosts: Optional[int] = Field(None, description="Number of connected hosts")
    host_info: List[HostInfo] = Field(default_factory=list, description="Detailed information about each connected host")
    wan_ethernet_stats: Optional[EthernetStats] = Field(None, description="Ethernet traffic statistics for the WAN interface")
    lan_ethernet_stats: List[EthernetStats] = Field(default_factory=list, description="Ethernet traffic statistics for each LAN interface")
    wifi_stats: List[WiFiStats] = Field(default_factory=list, description="WiFi traffic statistics for each WiFi interface")

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

