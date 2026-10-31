from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class FlowRule:
    rule_id: str
    target_ip: str
    action_type: str
    match_fields: Dict[str, Any]
    instruction: str
    priority: int
    duration_sec: Optional[int]
    created_at: datetime
    expires_at: Optional[datetime]
    packet_count: int = 0
    byte_count: int = 0

@dataclass
class NetworkAdapterExecutionResult:
    success: bool
    rule_id: str
    action_type: str
    target_ip: str
    adapter_mode: str # "RYU_SDN" or "MOCK"
    details: str
    duration_sec: Optional[int] = None
    created_at: datetime = datetime.utcnow()

class INetworkAdapter(ABC):
    """
    Abstract Network Adapter Interface for SDN response enforcement.
    Implemented by RyuOpenFlowAdapter (live Linux SDN) and MockNetworkAdapter (Windows dev).
    """
    @abstractmethod
    def apply_block_rule(self, target_ip: str, duration_sec: Optional[int] = None) -> NetworkAdapterExecutionResult:
        pass

    @abstractmethod
    def apply_rate_limit(self, target_ip: str, rate_kbps: int = 500, duration_sec: Optional[int] = None) -> NetworkAdapterExecutionResult:
        pass

    @abstractmethod
    def isolate_host(self, target_ip: str) -> NetworkAdapterExecutionResult:
        pass

    @abstractmethod
    def remove_rule(self, rule_id: str) -> NetworkAdapterExecutionResult:
        pass

    @abstractmethod
    def get_flow_table(self) -> List[FlowRule]:
        pass

    @abstractmethod
    def get_network_metrics(self) -> Dict[str, float]:
        pass

