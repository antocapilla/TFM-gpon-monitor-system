from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class WAN(BaseModel):
    index: str
    connectionStatus: str
    externalIPAddress: str
    name: str
    natEnabled: bool
    addressingType: str
    bytesReceived: int
    bytesSent: int
    uptime: int
    connectedWLANs: List[str]

class WiFiInterface(BaseModel):
    interfaceIndex: str
    ssid: str
    enable: bool
    status: str
    channel: int
    totalAssociations: int
    totalBytesReceived: int
    totalBytesSent: int

class Host(BaseModel):
    hostIndex: str
    active: bool
    addressSource: str
    clientID: str
    hostName: str
    iPAddress: str
    interfaceType: str
    wlanId: Optional[str]
    leaseTimeRemaining: int
    macAddress: str
    userClassID: str
    vendorClassID: str

class DeviceInfo(BaseModel):
    softwareVersion: str
    # upTime: int

class GPONInfo(BaseModel):
    biasCurrent: int
    rxPower: int
    status: str
    txPower: int
    transceiverTemperature: int

class ONTData(BaseModel):
    serial: str = Field(..., description="Unique identifier of the device")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the monitoring data")
    wans: List[WAN] = Field(default_factory=list, description="List of WAN interfaces")
    wifi: List[WiFiInterface] = Field(default_factory=list, description="List of WiFi interfaces")
    hosts: List[Host] = Field(default_factory=list, description="List of connected hosts")
    deviceInfo: DeviceInfo = Field(..., description="Device information")
    gpon: Optional[GPONInfo] = Field(None, description="GPON information")
    floor: Optional[str] = Field(None, description="Floor where the ONT is located")
    building: Optional[str] = Field(None, description="Building where the ONT is located")


class MonitoringConfig(BaseModel):
    enabled: bool = True
    interval: int = 300  # in seconds   