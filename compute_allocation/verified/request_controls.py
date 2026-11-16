from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from compute_allocation.requests.application import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        return float(sum(ord(ch) for ch in text) % 101)

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_requestor_country_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_requestor_country_presence_threshold', 10.333)
    return _result('check_requestor_country_presence', adjusted, threshold, True, 'validates requestor_country presence',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_requestor_country_range_threshold', 12.667)
    return _result('check_requestor_country_range', adjusted, threshold, True, 'validates requestor_country range',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_requestor_country_stability_threshold', 15.0)
    return _result('check_requestor_country_stability', adjusted, threshold, False, 'validates requestor_country stability',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_requestor_country_freshness_threshold', 17.333)
    return _result('check_requestor_country_freshness', adjusted, threshold, True, 'validates requestor_country freshness',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_requestor_country_coverage_threshold', 19.667)
    return _result('check_requestor_country_coverage', adjusted, threshold, True, 'validates requestor_country coverage',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_requestor_country_consistency_threshold', 22.0)
    return _result('check_requestor_country_consistency', adjusted, threshold, False, 'validates requestor_country consistency',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_requestor_country_risk_threshold', 24.333)
    return _result('check_requestor_country_risk', adjusted, threshold, True, 'validates requestor_country risk',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_requestor_country_confidence_threshold', 26.667)
    return _result('check_requestor_country_confidence', adjusted, threshold, True, 'validates requestor_country confidence',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_requestor_country_dependency_threshold', 29.0)
    return _result('check_requestor_country_dependency', adjusted, threshold, False, 'validates requestor_country dependency',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requestor_country_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requestor_country')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_requestor_country_readiness_threshold', 31.333)
    return _result('check_requestor_country_readiness', adjusted, threshold, True, 'validates requestor_country readiness',
                   {'field': 'requestor_country', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_use_case_presence_threshold', 9.333)
    return _result('check_use_case_presence', adjusted, threshold, True, 'validates use_case presence',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_use_case_range_threshold', 11.667)
    return _result('check_use_case_range', adjusted, threshold, False, 'validates use_case range',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_use_case_stability_threshold', 14.0)
    return _result('check_use_case_stability', adjusted, threshold, True, 'validates use_case stability',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_use_case_freshness_threshold', 16.333)
    return _result('check_use_case_freshness', adjusted, threshold, True, 'validates use_case freshness',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_use_case_coverage_threshold', 18.667)
    return _result('check_use_case_coverage', adjusted, threshold, False, 'validates use_case coverage',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_use_case_consistency_threshold', 21.0)
    return _result('check_use_case_consistency', adjusted, threshold, True, 'validates use_case consistency',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_use_case_risk_threshold', 23.333)
    return _result('check_use_case_risk', adjusted, threshold, True, 'validates use_case risk',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_use_case_confidence_threshold', 25.667)
    return _result('check_use_case_confidence', adjusted, threshold, False, 'validates use_case confidence',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_use_case_dependency_threshold', 28.0)
    return _result('check_use_case_dependency', adjusted, threshold, True, 'validates use_case dependency',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_use_case_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'use_case')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_use_case_readiness_threshold', 30.333)
    return _result('check_use_case_readiness', adjusted, threshold, True, 'validates use_case readiness',
                   {'field': 'use_case', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_public_value_proof_presence_threshold', 8.333)
    return _result('check_public_value_proof_presence', adjusted, threshold, False, 'validates public_value_proof presence',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_public_value_proof_range_threshold', 10.667)
    return _result('check_public_value_proof_range', adjusted, threshold, True, 'validates public_value_proof range',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_public_value_proof_stability_threshold', 13.0)
    return _result('check_public_value_proof_stability', adjusted, threshold, True, 'validates public_value_proof stability',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_public_value_proof_freshness_threshold', 15.333)
    return _result('check_public_value_proof_freshness', adjusted, threshold, False, 'validates public_value_proof freshness',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_public_value_proof_coverage_threshold', 17.667)
    return _result('check_public_value_proof_coverage', adjusted, threshold, True, 'validates public_value_proof coverage',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_public_value_proof_consistency_threshold', 20.0)
    return _result('check_public_value_proof_consistency', adjusted, threshold, True, 'validates public_value_proof consistency',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_public_value_proof_risk_threshold', 22.333)
    return _result('check_public_value_proof_risk', adjusted, threshold, False, 'validates public_value_proof risk',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_public_value_proof_confidence_threshold', 24.667)
    return _result('check_public_value_proof_confidence', adjusted, threshold, True, 'validates public_value_proof confidence',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_public_value_proof_dependency_threshold', 27.0)
    return _result('check_public_value_proof_dependency', adjusted, threshold, True, 'validates public_value_proof dependency',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_public_value_proof_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'public_value_proof')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_public_value_proof_readiness_threshold', 29.333)
    return _result('check_public_value_proof_readiness', adjusted, threshold, False, 'validates public_value_proof readiness',
                   {'field': 'public_value_proof', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_resource_gap_presence_threshold', 31.667)
    return _result('check_resource_gap_presence', adjusted, threshold, True, 'validates resource_gap presence',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_resource_gap_range_threshold', 9.667)
    return _result('check_resource_gap_range', adjusted, threshold, True, 'validates resource_gap range',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_resource_gap_stability_threshold', 12.0)
    return _result('check_resource_gap_stability', adjusted, threshold, False, 'validates resource_gap stability',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_resource_gap_freshness_threshold', 14.333)
    return _result('check_resource_gap_freshness', adjusted, threshold, True, 'validates resource_gap freshness',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_resource_gap_coverage_threshold', 16.667)
    return _result('check_resource_gap_coverage', adjusted, threshold, True, 'validates resource_gap coverage',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_resource_gap_consistency_threshold', 19.0)
    return _result('check_resource_gap_consistency', adjusted, threshold, False, 'validates resource_gap consistency',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_resource_gap_risk_threshold', 21.333)
    return _result('check_resource_gap_risk', adjusted, threshold, True, 'validates resource_gap risk',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_resource_gap_confidence_threshold', 23.667)
    return _result('check_resource_gap_confidence', adjusted, threshold, True, 'validates resource_gap confidence',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_resource_gap_dependency_threshold', 26.0)
    return _result('check_resource_gap_dependency', adjusted, threshold, False, 'validates resource_gap dependency',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_resource_gap_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'resource_gap')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_resource_gap_readiness_threshold', 28.333)
    return _result('check_resource_gap_readiness', adjusted, threshold, True, 'validates resource_gap readiness',
                   {'field': 'resource_gap', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_partner_assurance_presence_threshold', 30.667)
    return _result('check_partner_assurance_presence', adjusted, threshold, True, 'validates partner_assurance presence',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_partner_assurance_range_threshold', 8.667)
    return _result('check_partner_assurance_range', adjusted, threshold, False, 'validates partner_assurance range',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_partner_assurance_stability_threshold', 11.0)
    return _result('check_partner_assurance_stability', adjusted, threshold, True, 'validates partner_assurance stability',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_partner_assurance_freshness_threshold', 13.333)
    return _result('check_partner_assurance_freshness', adjusted, threshold, True, 'validates partner_assurance freshness',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_partner_assurance_coverage_threshold', 15.667)
    return _result('check_partner_assurance_coverage', adjusted, threshold, False, 'validates partner_assurance coverage',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_partner_assurance_consistency_threshold', 18.0)
    return _result('check_partner_assurance_consistency', adjusted, threshold, True, 'validates partner_assurance consistency',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_partner_assurance_risk_threshold', 20.333)
    return _result('check_partner_assurance_risk', adjusted, threshold, True, 'validates partner_assurance risk',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_partner_assurance_confidence_threshold', 22.667)
    return _result('check_partner_assurance_confidence', adjusted, threshold, False, 'validates partner_assurance confidence',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_partner_assurance_dependency_threshold', 25.0)
    return _result('check_partner_assurance_dependency', adjusted, threshold, True, 'validates partner_assurance dependency',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_partner_assurance_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'partner_assurance')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_partner_assurance_readiness_threshold', 27.333)
    return _result('check_partner_assurance_readiness', adjusted, threshold, True, 'validates partner_assurance readiness',
                   {'field': 'partner_assurance', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_localization_effort_presence_threshold', 29.667)
    return _result('check_localization_effort_presence', adjusted, threshold, False, 'validates localization_effort presence',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_localization_effort_range_threshold', 32.0)
    return _result('check_localization_effort_range', adjusted, threshold, True, 'validates localization_effort range',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_localization_effort_stability_threshold', 10.0)
    return _result('check_localization_effort_stability', adjusted, threshold, True, 'validates localization_effort stability',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_localization_effort_freshness_threshold', 12.333)
    return _result('check_localization_effort_freshness', adjusted, threshold, False, 'validates localization_effort freshness',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_localization_effort_coverage_threshold', 14.667)
    return _result('check_localization_effort_coverage', adjusted, threshold, True, 'validates localization_effort coverage',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_localization_effort_consistency_threshold', 17.0)
    return _result('check_localization_effort_consistency', adjusted, threshold, True, 'validates localization_effort consistency',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_localization_effort_risk_threshold', 19.333)
    return _result('check_localization_effort_risk', adjusted, threshold, False, 'validates localization_effort risk',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_localization_effort_confidence_threshold', 21.667)
    return _result('check_localization_effort_confidence', adjusted, threshold, True, 'validates localization_effort confidence',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_localization_effort_dependency_threshold', 24.0)
    return _result('check_localization_effort_dependency', adjusted, threshold, True, 'validates localization_effort dependency',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_localization_effort_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'localization_effort')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_localization_effort_readiness_threshold', 26.333)
    return _result('check_localization_effort_readiness', adjusted, threshold, False, 'validates localization_effort readiness',
                   {'field': 'localization_effort', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_delivery_capacity_presence_threshold', 28.667)
    return _result('check_delivery_capacity_presence', adjusted, threshold, True, 'validates delivery_capacity presence',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_delivery_capacity_range_threshold', 31.0)
    return _result('check_delivery_capacity_range', adjusted, threshold, True, 'validates delivery_capacity range',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_delivery_capacity_stability_threshold', 9.0)
    return _result('check_delivery_capacity_stability', adjusted, threshold, False, 'validates delivery_capacity stability',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_delivery_capacity_freshness_threshold', 11.333)
    return _result('check_delivery_capacity_freshness', adjusted, threshold, True, 'validates delivery_capacity freshness',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_delivery_capacity_coverage_threshold', 13.667)
    return _result('check_delivery_capacity_coverage', adjusted, threshold, True, 'validates delivery_capacity coverage',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_delivery_capacity_consistency_threshold', 16.0)
    return _result('check_delivery_capacity_consistency', adjusted, threshold, False, 'validates delivery_capacity consistency',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_delivery_capacity_risk_threshold', 18.333)
    return _result('check_delivery_capacity_risk', adjusted, threshold, True, 'validates delivery_capacity risk',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_delivery_capacity_confidence_threshold', 20.667)
    return _result('check_delivery_capacity_confidence', adjusted, threshold, True, 'validates delivery_capacity confidence',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_delivery_capacity_dependency_threshold', 23.0)
    return _result('check_delivery_capacity_dependency', adjusted, threshold, False, 'validates delivery_capacity dependency',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_delivery_capacity_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'delivery_capacity')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_delivery_capacity_readiness_threshold', 25.333)
    return _result('check_delivery_capacity_readiness', adjusted, threshold, True, 'validates delivery_capacity readiness',
                   {'field': 'delivery_capacity', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_requested_units_presence_threshold', 27.667)
    return _result('check_requested_units_presence', adjusted, threshold, True, 'validates requested_units presence',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_requested_units_range_threshold', 30.0)
    return _result('check_requested_units_range', adjusted, threshold, False, 'validates requested_units range',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_requested_units_stability_threshold', 8.0)
    return _result('check_requested_units_stability', adjusted, threshold, True, 'validates requested_units stability',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_requested_units_freshness_threshold', 10.333)
    return _result('check_requested_units_freshness', adjusted, threshold, True, 'validates requested_units freshness',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_requested_units_coverage_threshold', 12.667)
    return _result('check_requested_units_coverage', adjusted, threshold, False, 'validates requested_units coverage',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_requested_units_consistency_threshold', 15.0)
    return _result('check_requested_units_consistency', adjusted, threshold, True, 'validates requested_units consistency',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_requested_units_risk_threshold', 17.333)
    return _result('check_requested_units_risk', adjusted, threshold, True, 'validates requested_units risk',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_requested_units_confidence_threshold', 19.667)
    return _result('check_requested_units_confidence', adjusted, threshold, False, 'validates requested_units confidence',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_requested_units_dependency_threshold', 22.0)
    return _result('check_requested_units_dependency', adjusted, threshold, True, 'validates requested_units dependency',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_requested_units_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'requested_units')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_requested_units_readiness_threshold', 24.333)
    return _result('check_requested_units_readiness', adjusted, threshold, True, 'validates requested_units readiness',
                   {'field': 'requested_units', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_continuity_risk_presence_threshold', 26.667)
    return _result('check_continuity_risk_presence', adjusted, threshold, False, 'validates continuity_risk presence',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_continuity_risk_range_threshold', 29.0)
    return _result('check_continuity_risk_range', adjusted, threshold, True, 'validates continuity_risk range',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_continuity_risk_stability_threshold', 31.333)
    return _result('check_continuity_risk_stability', adjusted, threshold, True, 'validates continuity_risk stability',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_continuity_risk_freshness_threshold', 9.333)
    return _result('check_continuity_risk_freshness', adjusted, threshold, False, 'validates continuity_risk freshness',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_continuity_risk_coverage_threshold', 11.667)
    return _result('check_continuity_risk_coverage', adjusted, threshold, True, 'validates continuity_risk coverage',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_continuity_risk_consistency_threshold', 14.0)
    return _result('check_continuity_risk_consistency', adjusted, threshold, True, 'validates continuity_risk consistency',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_continuity_risk_risk_threshold', 16.333)
    return _result('check_continuity_risk_risk', adjusted, threshold, False, 'validates continuity_risk risk',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_continuity_risk_confidence_threshold', 18.667)
    return _result('check_continuity_risk_confidence', adjusted, threshold, True, 'validates continuity_risk confidence',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_continuity_risk_dependency_threshold', 21.0)
    return _result('check_continuity_risk_dependency', adjusted, threshold, True, 'validates continuity_risk dependency',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_continuity_risk_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'continuity_risk')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_continuity_risk_readiness_threshold', 23.333)
    return _result('check_continuity_risk_readiness', adjusted, threshold, False, 'validates continuity_risk readiness',
                   {'field': 'continuity_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_policy_risk_presence_threshold', 25.667)
    return _result('check_policy_risk_presence', adjusted, threshold, True, 'validates policy_risk presence',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_policy_risk_range_threshold', 28.0)
    return _result('check_policy_risk_range', adjusted, threshold, True, 'validates policy_risk range',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_policy_risk_stability_threshold', 30.333)
    return _result('check_policy_risk_stability', adjusted, threshold, False, 'validates policy_risk stability',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_policy_risk_freshness_threshold', 8.333)
    return _result('check_policy_risk_freshness', adjusted, threshold, True, 'validates policy_risk freshness',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_policy_risk_coverage_threshold', 10.667)
    return _result('check_policy_risk_coverage', adjusted, threshold, True, 'validates policy_risk coverage',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_policy_risk_consistency_threshold', 13.0)
    return _result('check_policy_risk_consistency', adjusted, threshold, False, 'validates policy_risk consistency',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_policy_risk_risk_threshold', 15.333)
    return _result('check_policy_risk_risk', adjusted, threshold, True, 'validates policy_risk risk',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_policy_risk_confidence_threshold', 17.667)
    return _result('check_policy_risk_confidence', adjusted, threshold, True, 'validates policy_risk confidence',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_policy_risk_dependency_threshold', 20.0)
    return _result('check_policy_risk_dependency', adjusted, threshold, False, 'validates policy_risk dependency',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_policy_risk_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'policy_risk')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_policy_risk_readiness_threshold', 22.333)
    return _result('check_policy_risk_readiness', adjusted, threshold, True, 'validates policy_risk readiness',
                   {'field': 'policy_risk', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_operations_cost_presence_threshold', 24.667)
    return _result('check_operations_cost_presence', adjusted, threshold, True, 'validates operations_cost presence',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_operations_cost_range_threshold', 27.0)
    return _result('check_operations_cost_range', adjusted, threshold, False, 'validates operations_cost range',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_operations_cost_stability_threshold', 29.333)
    return _result('check_operations_cost_stability', adjusted, threshold, True, 'validates operations_cost stability',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_operations_cost_freshness_threshold', 31.667)
    return _result('check_operations_cost_freshness', adjusted, threshold, True, 'validates operations_cost freshness',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_operations_cost_coverage_threshold', 9.667)
    return _result('check_operations_cost_coverage', adjusted, threshold, False, 'validates operations_cost coverage',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_operations_cost_consistency_threshold', 12.0)
    return _result('check_operations_cost_consistency', adjusted, threshold, True, 'validates operations_cost consistency',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_operations_cost_risk_threshold', 14.333)
    return _result('check_operations_cost_risk', adjusted, threshold, True, 'validates operations_cost risk',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_operations_cost_confidence_threshold', 16.667)
    return _result('check_operations_cost_confidence', adjusted, threshold, False, 'validates operations_cost confidence',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_operations_cost_dependency_threshold', 19.0)
    return _result('check_operations_cost_dependency', adjusted, threshold, True, 'validates operations_cost dependency',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_operations_cost_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'operations_cost')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_operations_cost_readiness_threshold', 21.333)
    return _result('check_operations_cost_readiness', adjusted, threshold, True, 'validates operations_cost readiness',
                   {'field': 'operations_cost', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_dependency_count_presence_threshold', 23.667)
    return _result('check_dependency_count_presence', adjusted, threshold, False, 'validates dependency_count presence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_dependency_count_range_threshold', 26.0)
    return _result('check_dependency_count_range', adjusted, threshold, True, 'validates dependency_count range',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_dependency_count_stability_threshold', 28.333)
    return _result('check_dependency_count_stability', adjusted, threshold, True, 'validates dependency_count stability',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_dependency_count_freshness_threshold', 30.667)
    return _result('check_dependency_count_freshness', adjusted, threshold, False, 'validates dependency_count freshness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_dependency_count_coverage_threshold', 8.667)
    return _result('check_dependency_count_coverage', adjusted, threshold, True, 'validates dependency_count coverage',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_dependency_count_consistency_threshold', 11.0)
    return _result('check_dependency_count_consistency', adjusted, threshold, True, 'validates dependency_count consistency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_dependency_count_risk_threshold', 13.333)
    return _result('check_dependency_count_risk', adjusted, threshold, False, 'validates dependency_count risk',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_dependency_count_confidence_threshold', 15.667)
    return _result('check_dependency_count_confidence', adjusted, threshold, True, 'validates dependency_count confidence',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_dependency_count_dependency_threshold', 18.0)
    return _result('check_dependency_count_dependency', adjusted, threshold, True, 'validates dependency_count dependency',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_dependency_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'dependency_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_dependency_count_readiness_threshold', 20.333)
    return _result('check_dependency_count_readiness', adjusted, threshold, False, 'validates dependency_count readiness',
                   {'field': 'dependency_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_requestor_country_presence,
    check_requestor_country_range,
    check_requestor_country_stability,
    check_requestor_country_freshness,
    check_requestor_country_coverage,
    check_requestor_country_consistency,
    check_requestor_country_risk,
    check_requestor_country_confidence,
    check_requestor_country_dependency,
    check_requestor_country_readiness,
    check_use_case_presence,
    check_use_case_range,
    check_use_case_stability,
    check_use_case_freshness,
    check_use_case_coverage,
    check_use_case_consistency,
    check_use_case_risk,
    check_use_case_confidence,
    check_use_case_dependency,
    check_use_case_readiness,
    check_public_value_proof_presence,
    check_public_value_proof_range,
    check_public_value_proof_stability,
    check_public_value_proof_freshness,
    check_public_value_proof_coverage,
    check_public_value_proof_consistency,
    check_public_value_proof_risk,
    check_public_value_proof_confidence,
    check_public_value_proof_dependency,
    check_public_value_proof_readiness,
    check_resource_gap_presence,
    check_resource_gap_range,
    check_resource_gap_stability,
    check_resource_gap_freshness,
    check_resource_gap_coverage,
    check_resource_gap_consistency,
    check_resource_gap_risk,
    check_resource_gap_confidence,
    check_resource_gap_dependency,
    check_resource_gap_readiness,
    check_partner_assurance_presence,
    check_partner_assurance_range,
    check_partner_assurance_stability,
    check_partner_assurance_freshness,
    check_partner_assurance_coverage,
    check_partner_assurance_consistency,
    check_partner_assurance_risk,
    check_partner_assurance_confidence,
    check_partner_assurance_dependency,
    check_partner_assurance_readiness,
    check_localization_effort_presence,
    check_localization_effort_range,
    check_localization_effort_stability,
    check_localization_effort_freshness,
    check_localization_effort_coverage,
    check_localization_effort_consistency,
    check_localization_effort_risk,
    check_localization_effort_confidence,
    check_localization_effort_dependency,
    check_localization_effort_readiness,
    check_delivery_capacity_presence,
    check_delivery_capacity_range,
    check_delivery_capacity_stability,
    check_delivery_capacity_freshness,
    check_delivery_capacity_coverage,
    check_delivery_capacity_consistency,
    check_delivery_capacity_risk,
    check_delivery_capacity_confidence,
    check_delivery_capacity_dependency,
    check_delivery_capacity_readiness,
    check_requested_units_presence,
    check_requested_units_range,
    check_requested_units_stability,
    check_requested_units_freshness,
    check_requested_units_coverage,
    check_requested_units_consistency,
    check_requested_units_risk,
    check_requested_units_confidence,
    check_requested_units_dependency,
    check_requested_units_readiness,
    check_continuity_risk_presence,
    check_continuity_risk_range,
    check_continuity_risk_stability,
    check_continuity_risk_freshness,
    check_continuity_risk_coverage,
    check_continuity_risk_consistency,
    check_continuity_risk_risk,
    check_continuity_risk_confidence,
    check_continuity_risk_dependency,
    check_continuity_risk_readiness,
    check_policy_risk_presence,
    check_policy_risk_range,
    check_policy_risk_stability,
    check_policy_risk_freshness,
    check_policy_risk_coverage,
    check_policy_risk_consistency,
    check_policy_risk_risk,
    check_policy_risk_confidence,
    check_policy_risk_dependency,
    check_policy_risk_readiness,
    check_operations_cost_presence,
    check_operations_cost_range,
    check_operations_cost_stability,
    check_operations_cost_freshness,
    check_operations_cost_coverage,
    check_operations_cost_consistency,
    check_operations_cost_risk,
    check_operations_cost_confidence,
    check_operations_cost_dependency,
    check_operations_cost_readiness,
    check_dependency_count_presence,
    check_dependency_count_range,
    check_dependency_count_stability,
    check_dependency_count_freshness,
    check_dependency_count_coverage,
    check_dependency_count_consistency,
    check_dependency_count_risk,
    check_dependency_count_confidence,
    check_dependency_count_dependency,
    check_dependency_count_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}
