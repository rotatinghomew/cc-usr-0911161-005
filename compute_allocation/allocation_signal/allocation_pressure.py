from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def allocation_pressure(payload: Mapping[str, Any]) -> DomainSignal:
    public_value = ratio(payload, 'public_value_proof')
    gap = ratio(payload, 'resource_gap')
    assurance = ratio(payload, 'partner_assurance')
    delivery = ratio(payload, 'delivery_capacity')
    requested = max(0.0, number(payload, 'requested_units'))
    operations = max(0.0, number(payload, 'operations_cost'))
    continuity = ratio(payload, 'continuity_risk')
    policy = ratio(payload, 'policy_risk')
    dependencies = min(1.0, number(payload, 'dependency_count') / 20.0)
    capacity_fit = min(1.0, delivery / max(0.01, requested / 100.0))
    burden = min(1.0, operations / max(1.0, requested))
    score = clamp(public_value*0.26 + gap*0.18 + assurance*0.14 + capacity_fit*0.18 + (1-continuity)*0.08 + (1-policy)*0.08 + (1-burden)*0.04 + (1-dependencies)*0.04)
    severity = 'critical' if capacity_fit < 0.25 or requested <= 0 else 'warning' if continuity + policy > 1.2 else 'info'
    return DomainSignal('allocation_pressure', score, severity, {'capacity_fit': capacity_fit, 'burden': burden, 'requested_units': requested, 'risk_total': continuity+policy})

def peer_distribution(records: Iterable[Any], group_field: str = 'requestor_country') -> dict[str, Any]:
    totals = {}
    for record in records:
        payload = getattr(record, 'payload', record); key = str(payload.get(group_field, 'unknown'))
        totals[key] = totals.get(key, 0.0) + number(payload, 'requested_units')
    grand = sum(totals.values()); concentration = max(totals.values())/grand if totals and grand else 0.0
    return {'country_units': totals, 'total_units': grand, 'concentration': concentration, 'count': len(totals)}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal = allocation_pressure(record.payload); peers = peer_distribution(repository.list_records())
    return {'domain_signal': signal.score, 'domain_severity': signal.severity, 'allocation_concentration': peers['concentration'], 'requested_total': peers['total_units']}
