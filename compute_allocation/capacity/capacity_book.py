from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Callable, Iterable, Mapping

from compute_allocation.requests.application import DomainRecord, bounded, finite_number, normalized_text, stable_hash
from compute_allocation.verified.request_controls import evaluate, summarize

MetricFunction = Callable[[DomainRecord, Mapping[str, Any]], float]

def _value(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    return float(sum((index + 1) * ord(ch) for index, ch in enumerate(text)) % 997) / 10.0

def _signal(record: DomainRecord, fields: tuple[str, ...], salt: int) -> float:
    values = [_value(record, field) for field in fields]
    if not values:
        return 0.0
    center = statistics.fmean(values)
    spread = statistics.pstdev(values) if len(values) > 1 else 0.0
    harmonic = sum(math.sin(value / (salt + 1)) + math.cos(value * (salt + 1) / 17.0) for value in values)
    return bounded(0.5 + math.tanh((center - spread + harmonic) / (30.0 + salt)) / 2.0)

def metric_readiness_index_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 1)
    weight = finite_number(context.get('readiness_index_weight', 0.7))
    offset = finite_number(context.get('metric_readiness_index_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_readiness_index_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 2)
    weight = finite_number(context.get('readiness_index_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_readiness_index_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_readiness_index_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 3)
    weight = finite_number(context.get('readiness_index_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_readiness_index_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_readiness_index_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 4)
    weight = finite_number(context.get('readiness_index_weight', 1.0))
    offset = finite_number(context.get('metric_readiness_index_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_readiness_index_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 5)
    weight = finite_number(context.get('readiness_index_weight', 0.7))
    offset = finite_number(context.get('metric_readiness_index_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_readiness_index_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('readiness_index_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_readiness_index_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_readiness_index_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('readiness_index_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_readiness_index_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_readiness_index_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('readiness_index_weight', 1.0))
    offset = finite_number(context.get('metric_readiness_index_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_readiness_index_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('readiness_index_weight', 0.7))
    offset = finite_number(context.get('metric_readiness_index_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_readiness_index_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('readiness_index_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_readiness_index_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_evidence_diversity_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 2)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_diversity_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_evidence_diversity_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 3)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_diversity_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_evidence_diversity_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 4)
    weight = finite_number(context.get('evidence_diversity_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_evidence_diversity_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_evidence_diversity_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 5)
    weight = finite_number(context.get('evidence_diversity_weight', 1.0))
    offset = finite_number(context.get('metric_evidence_diversity_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_evidence_diversity_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_diversity_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_evidence_diversity_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_diversity_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_evidence_diversity_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('evidence_diversity_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_evidence_diversity_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_evidence_diversity_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('evidence_diversity_weight', 1.0))
    offset = finite_number(context.get('metric_evidence_diversity_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_evidence_diversity_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7))
    offset = finite_number(context.get('metric_evidence_diversity_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_evidence_diversity_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('evidence_diversity_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_evidence_diversity_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_concentration_risk_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 3)
    weight = finite_number(context.get('concentration_risk_weight', 0.7))
    offset = finite_number(context.get('metric_concentration_risk_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_concentration_risk_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 4)
    weight = finite_number(context.get('concentration_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_concentration_risk_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_concentration_risk_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 5)
    weight = finite_number(context.get('concentration_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_concentration_risk_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_concentration_risk_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('concentration_risk_weight', 1.0))
    offset = finite_number(context.get('metric_concentration_risk_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_concentration_risk_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('concentration_risk_weight', 0.7))
    offset = finite_number(context.get('metric_concentration_risk_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_concentration_risk_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('concentration_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_concentration_risk_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_concentration_risk_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('concentration_risk_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_concentration_risk_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_concentration_risk_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('concentration_risk_weight', 1.0))
    offset = finite_number(context.get('metric_concentration_risk_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_concentration_risk_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('concentration_risk_weight', 0.7))
    offset = finite_number(context.get('metric_concentration_risk_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_concentration_risk_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('concentration_risk_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_concentration_risk_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_capacity_fit_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 4)
    weight = finite_number(context.get('capacity_fit_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_fit_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_capacity_fit_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 5)
    weight = finite_number(context.get('capacity_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_fit_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_capacity_fit_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('capacity_fit_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_fit_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_capacity_fit_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('capacity_fit_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_fit_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_capacity_fit_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('capacity_fit_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_fit_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_capacity_fit_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('capacity_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_fit_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_capacity_fit_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('capacity_fit_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_capacity_fit_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_capacity_fit_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('capacity_fit_weight', 1.0))
    offset = finite_number(context.get('metric_capacity_fit_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_capacity_fit_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('capacity_fit_weight', 0.7))
    offset = finite_number(context.get('metric_capacity_fit_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_capacity_fit_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 13)
    weight = finite_number(context.get('capacity_fit_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_capacity_fit_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_commercial_resilience_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 5)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_commercial_resilience_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_commercial_resilience_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_commercial_resilience_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_commercial_resilience_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('commercial_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_commercial_resilience_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_commercial_resilience_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('commercial_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_commercial_resilience_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_commercial_resilience_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_commercial_resilience_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_commercial_resilience_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_commercial_resilience_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_commercial_resilience_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('commercial_resilience_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_commercial_resilience_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_commercial_resilience_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('commercial_resilience_weight', 1.0))
    offset = finite_number(context.get('metric_commercial_resilience_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_commercial_resilience_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 13)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7))
    offset = finite_number(context.get('metric_commercial_resilience_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_commercial_resilience_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 14)
    weight = finite_number(context.get('commercial_resilience_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_commercial_resilience_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_policy_exposure_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('localization_effort', 'continuity_risk', 'dependency_count', 'public_value_proof'), 6)
    weight = finite_number(context.get('policy_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_policy_exposure_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_policy_exposure_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('policy_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_policy_exposure_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_policy_exposure_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('policy_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_policy_exposure_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_policy_exposure_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('policy_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_policy_exposure_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_policy_exposure_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('policy_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_policy_exposure_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_policy_exposure_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('policy_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_policy_exposure_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_policy_exposure_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('policy_exposure_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_policy_exposure_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_policy_exposure_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 13)
    weight = finite_number(context.get('policy_exposure_weight', 1.0))
    offset = finite_number(context.get('metric_policy_exposure_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_policy_exposure_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 14)
    weight = finite_number(context.get('policy_exposure_weight', 0.7))
    offset = finite_number(context.get('metric_policy_exposure_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_policy_exposure_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 15)
    weight = finite_number(context.get('policy_exposure_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_policy_exposure_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_dependency_fragility_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('delivery_capacity', 'policy_risk', 'requestor_country', 'resource_gap'), 7)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7))
    offset = finite_number(context.get('metric_dependency_fragility_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_dependency_fragility_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_dependency_fragility_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_dependency_fragility_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('dependency_fragility_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_dependency_fragility_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_dependency_fragility_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('dependency_fragility_weight', 1.0))
    offset = finite_number(context.get('metric_dependency_fragility_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_dependency_fragility_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7))
    offset = finite_number(context.get('metric_dependency_fragility_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_dependency_fragility_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_dependency_fragility_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_dependency_fragility_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 13)
    weight = finite_number(context.get('dependency_fragility_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_dependency_fragility_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_dependency_fragility_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 14)
    weight = finite_number(context.get('dependency_fragility_weight', 1.0))
    offset = finite_number(context.get('metric_dependency_fragility_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_dependency_fragility_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 15)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7))
    offset = finite_number(context.get('metric_dependency_fragility_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_dependency_fragility_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 16)
    weight = finite_number(context.get('dependency_fragility_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_dependency_fragility_10_offset', 0.1))
    return bounded(base * weight + offset)

def metric_portfolio_value_01(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requested_units', 'operations_cost', 'use_case', 'partner_assurance'), 8)
    weight = finite_number(context.get('portfolio_value_weight', 0.7))
    offset = finite_number(context.get('metric_portfolio_value_01_offset', -0.08))
    return bounded(base * weight + offset)

def metric_portfolio_value_02(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('continuity_risk', 'dependency_count', 'public_value_proof', 'localization_effort'), 9)
    weight = finite_number(context.get('portfolio_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_portfolio_value_02_offset', -0.06))
    return bounded(base * weight + offset)

def metric_portfolio_value_03(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('policy_risk', 'requestor_country', 'resource_gap', 'delivery_capacity'), 10)
    weight = finite_number(context.get('portfolio_value_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_portfolio_value_03_offset', -0.04))
    return bounded(base * weight + offset)

def metric_portfolio_value_04(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('operations_cost', 'use_case', 'partner_assurance', 'requested_units'), 11)
    weight = finite_number(context.get('portfolio_value_weight', 1.0))
    offset = finite_number(context.get('metric_portfolio_value_04_offset', -0.02))
    return bounded(base * weight + offset)

def metric_portfolio_value_05(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('dependency_count', 'public_value_proof', 'localization_effort', 'continuity_risk'), 12)
    weight = finite_number(context.get('portfolio_value_weight', 0.7))
    offset = finite_number(context.get('metric_portfolio_value_05_offset', 0.0))
    return bounded(base * weight + offset)

def metric_portfolio_value_06(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('requestor_country', 'resource_gap', 'delivery_capacity', 'policy_risk'), 13)
    weight = finite_number(context.get('portfolio_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_portfolio_value_06_offset', 0.02))
    return bounded(base * weight + offset)

def metric_portfolio_value_07(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('use_case', 'partner_assurance', 'requested_units', 'operations_cost'), 14)
    weight = finite_number(context.get('portfolio_value_weight', 0.8999999999999999))
    offset = finite_number(context.get('metric_portfolio_value_07_offset', 0.04))
    return bounded(base * weight + offset)

def metric_portfolio_value_08(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('public_value_proof', 'localization_effort', 'continuity_risk', 'dependency_count'), 15)
    weight = finite_number(context.get('portfolio_value_weight', 1.0))
    offset = finite_number(context.get('metric_portfolio_value_08_offset', 0.06))
    return bounded(base * weight + offset)

def metric_portfolio_value_09(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('resource_gap', 'delivery_capacity', 'policy_risk', 'requestor_country'), 16)
    weight = finite_number(context.get('portfolio_value_weight', 0.7))
    offset = finite_number(context.get('metric_portfolio_value_09_offset', 0.08))
    return bounded(base * weight + offset)

def metric_portfolio_value_10(record: DomainRecord, context: Mapping[str, Any]) -> float:
    base = _signal(record, ('partner_assurance', 'requested_units', 'operations_cost', 'use_case'), 17)
    weight = finite_number(context.get('portfolio_value_weight', 0.7999999999999999))
    offset = finite_number(context.get('metric_portfolio_value_10_offset', 0.1))
    return bounded(base * weight + offset)

METRICS: dict[str, MetricFunction] = {
    'metric_readiness_index_01': metric_readiness_index_01,
    'metric_readiness_index_02': metric_readiness_index_02,
    'metric_readiness_index_03': metric_readiness_index_03,
    'metric_readiness_index_04': metric_readiness_index_04,
    'metric_readiness_index_05': metric_readiness_index_05,
    'metric_readiness_index_06': metric_readiness_index_06,
    'metric_readiness_index_07': metric_readiness_index_07,
    'metric_readiness_index_08': metric_readiness_index_08,
    'metric_readiness_index_09': metric_readiness_index_09,
    'metric_readiness_index_10': metric_readiness_index_10,
    'metric_evidence_diversity_01': metric_evidence_diversity_01,
    'metric_evidence_diversity_02': metric_evidence_diversity_02,
    'metric_evidence_diversity_03': metric_evidence_diversity_03,
    'metric_evidence_diversity_04': metric_evidence_diversity_04,
    'metric_evidence_diversity_05': metric_evidence_diversity_05,
    'metric_evidence_diversity_06': metric_evidence_diversity_06,
    'metric_evidence_diversity_07': metric_evidence_diversity_07,
    'metric_evidence_diversity_08': metric_evidence_diversity_08,
    'metric_evidence_diversity_09': metric_evidence_diversity_09,
    'metric_evidence_diversity_10': metric_evidence_diversity_10,
    'metric_concentration_risk_01': metric_concentration_risk_01,
    'metric_concentration_risk_02': metric_concentration_risk_02,
    'metric_concentration_risk_03': metric_concentration_risk_03,
    'metric_concentration_risk_04': metric_concentration_risk_04,
    'metric_concentration_risk_05': metric_concentration_risk_05,
    'metric_concentration_risk_06': metric_concentration_risk_06,
    'metric_concentration_risk_07': metric_concentration_risk_07,
    'metric_concentration_risk_08': metric_concentration_risk_08,
    'metric_concentration_risk_09': metric_concentration_risk_09,
    'metric_concentration_risk_10': metric_concentration_risk_10,
    'metric_capacity_fit_01': metric_capacity_fit_01,
    'metric_capacity_fit_02': metric_capacity_fit_02,
    'metric_capacity_fit_03': metric_capacity_fit_03,
    'metric_capacity_fit_04': metric_capacity_fit_04,
    'metric_capacity_fit_05': metric_capacity_fit_05,
    'metric_capacity_fit_06': metric_capacity_fit_06,
    'metric_capacity_fit_07': metric_capacity_fit_07,
    'metric_capacity_fit_08': metric_capacity_fit_08,
    'metric_capacity_fit_09': metric_capacity_fit_09,
    'metric_capacity_fit_10': metric_capacity_fit_10,
    'metric_commercial_resilience_01': metric_commercial_resilience_01,
    'metric_commercial_resilience_02': metric_commercial_resilience_02,
    'metric_commercial_resilience_03': metric_commercial_resilience_03,
    'metric_commercial_resilience_04': metric_commercial_resilience_04,
    'metric_commercial_resilience_05': metric_commercial_resilience_05,
    'metric_commercial_resilience_06': metric_commercial_resilience_06,
    'metric_commercial_resilience_07': metric_commercial_resilience_07,
    'metric_commercial_resilience_08': metric_commercial_resilience_08,
    'metric_commercial_resilience_09': metric_commercial_resilience_09,
    'metric_commercial_resilience_10': metric_commercial_resilience_10,
    'metric_policy_exposure_01': metric_policy_exposure_01,
    'metric_policy_exposure_02': metric_policy_exposure_02,
    'metric_policy_exposure_03': metric_policy_exposure_03,
    'metric_policy_exposure_04': metric_policy_exposure_04,
    'metric_policy_exposure_05': metric_policy_exposure_05,
    'metric_policy_exposure_06': metric_policy_exposure_06,
    'metric_policy_exposure_07': metric_policy_exposure_07,
    'metric_policy_exposure_08': metric_policy_exposure_08,
    'metric_policy_exposure_09': metric_policy_exposure_09,
    'metric_policy_exposure_10': metric_policy_exposure_10,
    'metric_dependency_fragility_01': metric_dependency_fragility_01,
    'metric_dependency_fragility_02': metric_dependency_fragility_02,
    'metric_dependency_fragility_03': metric_dependency_fragility_03,
    'metric_dependency_fragility_04': metric_dependency_fragility_04,
    'metric_dependency_fragility_05': metric_dependency_fragility_05,
    'metric_dependency_fragility_06': metric_dependency_fragility_06,
    'metric_dependency_fragility_07': metric_dependency_fragility_07,
    'metric_dependency_fragility_08': metric_dependency_fragility_08,
    'metric_dependency_fragility_09': metric_dependency_fragility_09,
    'metric_dependency_fragility_10': metric_dependency_fragility_10,
    'metric_portfolio_value_01': metric_portfolio_value_01,
    'metric_portfolio_value_02': metric_portfolio_value_02,
    'metric_portfolio_value_03': metric_portfolio_value_03,
    'metric_portfolio_value_04': metric_portfolio_value_04,
    'metric_portfolio_value_05': metric_portfolio_value_05,
    'metric_portfolio_value_06': metric_portfolio_value_06,
    'metric_portfolio_value_07': metric_portfolio_value_07,
    'metric_portfolio_value_08': metric_portfolio_value_08,
    'metric_portfolio_value_09': metric_portfolio_value_09,
    'metric_portfolio_value_10': metric_portfolio_value_10,
}

def metric_vector(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    context = context or {}
    return {name: function(record, context) for name, function in METRICS.items()}

def grouped_metrics(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, float]:
    vector = metric_vector(record, context)
    groups: dict[str, list[float]] = defaultdict(list)
    for name, value in vector.items():
        key = name.rsplit('_', 1)[0].removeprefix('metric_')
        groups[key].append(value)
    return {key: statistics.fmean(values) for key, values in groups.items()}

def record_score(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    rules = evaluate(record, context)
    rule_summary = summarize(rules)
    metrics = grouped_metrics(record, context)
    metric_score = statistics.fmean(metrics.values()) if metrics else 0.0
    combined = bounded(rule_summary['score'] * 0.55 + metric_score * 0.45)
    return {'score': combined, 'rule_summary': rule_summary, 'metrics': metrics,
            'fingerprint': stable_hash({'record': record.fingerprint, 'metrics': metrics, 'rules': rule_summary})}

def portfolio(records: Iterable[DomainRecord], context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    rows = [record_score(record, context) | {'record_id': record.record_id} for record in records]
    if not rows:
        return {'count': 0, 'average': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'rows': []}
    scores = [row['score'] for row in rows]
    return {'count': len(rows), 'average': statistics.fmean(scores),
            'minimum': min(scores), 'maximum': max(scores), 'rows': sorted(rows, key=lambda row: (-row['score'], row['record_id']))}

def compare(left: DomainRecord, right: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    left_metrics = grouped_metrics(left, context)
    right_metrics = grouped_metrics(right, context)
    delta = {key: right_metrics.get(key, 0.0) - left_metrics.get(key, 0.0) for key in sorted(set(left_metrics) | set(right_metrics))}
    return {'left': left.record_id, 'right': right.record_id, 'delta': delta,
            'winner': right.record_id if sum(delta.values()) >= 0 else left.record_id}
