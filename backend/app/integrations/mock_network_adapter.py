import ipaddress
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.integrations.network_adapter_base import INetworkAdapter, FlowRule, NetworkAdapterExecutionResult

# Authorized academic lab subnets (includes RFC 5737 academic research testbeds)
AUTHORIZED_LAB_SUBNETS = [
    ipaddress.ip_network("10.0.0.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("203.0.113.0/24")
]

class MockNetworkAdapter(INetworkAdapter):
    """
    High-Fidelity Mock Network Adapter for Windows development and zero-cost simulation.
    Faithfully simulates OpenFlow 1.3 flow table insertion, switch flow counters,
    rate-limiting meters, and automatic rule expiration with strict subnet isolation safeguards.
    """
    def __init__(self):
        self.flow_rules: Dict[str, FlowRule] = {}
        self.active_mitigations: Dict[str, str] = {} # ip -> action_type
        # Simulated live baseline metrics
        self.current_attack_pps = 0.0
        self.legitimate_tp_mbps = 95.0
        self.latency_ms = 1.2
        self.packet_loss_pct = 0.1

    def _validate_lab_ip(self, ip_str: str) -> bool:
        """Safeguard: strictly verify that target IP is inside isolated academic lab range."""
        try:
            ip = ipaddress.ip_address(ip_str)
            return any(ip in subnet for subnet in AUTHORIZED_LAB_SUBNETS)
        except ValueError:
            return False

    def _purge_expired_rules(self):
        now = datetime.utcnow()
        expired_ids = [
            r_id for r_id, rule in self.flow_rules.items()
            if rule.expires_at and rule.expires_at <= now
        ]
        for r_id in expired_ids:
            rule = self.flow_rules.pop(r_id, None)
            if rule and rule.target_ip in self.active_mitigations:
                del self.active_mitigations[rule.target_ip]

    def apply_block_rule(self, target_ip: str, duration_sec: Optional[int] = None) -> NetworkAdapterExecutionResult:
        self._purge_expired_rules()
        if not self._validate_lab_ip(target_ip):
            return NetworkAdapterExecutionResult(
                success=False,
                rule_id="",
                action_type="BLOCK_IP",
                target_ip=target_ip,
                adapter_mode="MOCK",
                details=f"Security Safeguard: Target {target_ip} is outside authorized lab testbed ({AUTHORIZED_LAB_SUBNET}). Blocked."
            )

        rule_id = f"flow_block_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=duration_sec) if duration_sec else None

        rule = FlowRule(
            rule_id=rule_id,
            target_ip=target_ip,
            action_type="BLOCK_IP",
            match_fields={"ipv4_src": target_ip, "eth_type": 0x0800},
            instruction="DROP",
            priority=30000,
            duration_sec=duration_sec,
            created_at=now,
            expires_at=expires_at
        )

        self.flow_rules[rule_id] = rule
        self.active_mitigations[target_ip] = "BLOCK_IP"
        # Simulated impact: attack traffic nullified
        self.current_attack_pps = max(0.0, self.current_attack_pps * 0.01)

        return NetworkAdapterExecutionResult(
            success=True,
            rule_id=rule_id,
            action_type="BLOCK_IP",
            target_ip=target_ip,
            adapter_mode="MOCK",
            duration_sec=duration_sec,
            details=f"Simulated OpenFlow DROP flow installed for {target_ip} on Switch s1/s2 table 0 (Priority 30000)."
        )

    def apply_rate_limit(self, target_ip: str, rate_kbps: int = 500, duration_sec: Optional[int] = None) -> NetworkAdapterExecutionResult:
        self._purge_expired_rules()
        if not self._validate_lab_ip(target_ip):
            return NetworkAdapterExecutionResult(
                success=False,
                rule_id="",
                action_type="RATE_LIMIT",
                target_ip=target_ip,
                adapter_mode="MOCK",
                details=f"Security Safeguard: Target {target_ip} is outside authorized lab testbed."
            )

        rule_id = f"meter_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=duration_sec) if duration_sec else None

        rule = FlowRule(
            rule_id=rule_id,
            target_ip=target_ip,
            action_type="RATE_LIMIT",
            match_fields={"ipv4_src": target_ip, "rate_kbps": rate_kbps},
            instruction=f"APPLY_METER_{rate_kbps}KBPS",
            priority=25000,
            duration_sec=duration_sec,
            created_at=now,
            expires_at=expires_at
        )

        self.flow_rules[rule_id] = rule
        self.active_mitigations[target_ip] = "RATE_LIMIT"
        # Simulated impact: throttled
        self.current_attack_pps = min(50.0, self.current_attack_pps * 0.15)

        return NetworkAdapterExecutionResult(
            success=True,
            rule_id=rule_id,
            action_type="RATE_LIMIT",
            target_ip=target_ip,
            adapter_mode="MOCK",
            duration_sec=duration_sec,
            details=f"Simulated OpenFlow Meter {rate_kbps} kbps installed for {target_ip}."
        )

    def isolate_host(self, target_ip: str) -> NetworkAdapterExecutionResult:
        self._purge_expired_rules()
        if not self._validate_lab_ip(target_ip):
            return NetworkAdapterExecutionResult(
                success=False,
                rule_id="",
                action_type="ISOLATE_HOST",
                target_ip=target_ip,
                adapter_mode="MOCK",
                details=f"Security Safeguard: Target {target_ip} outside lab subnet."
            )

        rule_id = f"flow_isolate_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        rule = FlowRule(
            rule_id=rule_id,
            target_ip=target_ip,
            action_type="ISOLATE_HOST",
            match_fields={"ipv4_src": target_ip, "ipv4_dst": target_ip},
            instruction="DISCONNECT_VPORT",
            priority=40000,
            duration_sec=None,
            created_at=now,
            expires_at=None
        )

        self.flow_rules[rule_id] = rule
        self.active_mitigations[target_ip] = "ISOLATE_HOST"

        return NetworkAdapterExecutionResult(
            success=True,
            rule_id=rule_id,
            action_type="ISOLATE_HOST",
            target_ip=target_ip,
            adapter_mode="MOCK",
            details=f"Host {target_ip} fully isolated from virtual switch fabric."
        )

    def remove_rule(self, rule_id: str) -> NetworkAdapterExecutionResult:
        rule = self.flow_rules.pop(rule_id, None)
        if not rule:
            return NetworkAdapterExecutionResult(
                success=False,
                rule_id=rule_id,
                action_type="ROLLBACK",
                target_ip="",
                adapter_mode="MOCK",
                details=f"Rule {rule_id} not found or already expired."
            )

        if rule.target_ip in self.active_mitigations:
            del self.active_mitigations[rule.target_ip]

        return NetworkAdapterExecutionResult(
            success=True,
            rule_id=rule_id,
            action_type="ROLLBACK",
            target_ip=rule.target_ip,
            adapter_mode="MOCK",
            details=f"OpenFlow rule {rule_id} successfully purged from switch flow table. Normal forwarding restored."
        )

    def get_flow_table(self) -> List[FlowRule]:
        self._purge_expired_rules()
        return list(self.flow_rules.values())

    def get_network_metrics(self) -> Dict[str, float]:
        self._purge_expired_rules()
        return {
            "attack_pps": self.current_attack_pps,
            "legitimate_throughput_mbps": self.legitimate_tp_mbps,
            "latency_ms": self.latency_ms,
            "packet_loss_pct": self.packet_loss_pct,
            "active_rules_count": float(len(self.flow_rules))
        }

mock_adapter = MockNetworkAdapter()

