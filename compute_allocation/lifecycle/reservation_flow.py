from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from compute_allocation.requests.application import ContractError, Decision, DomainRecord, RuleResult, bounded
from compute_allocation.capacity.capacity_book import grouped_metrics, record_score
from compute_allocation.verified.request_controls import evaluate

STATES = ['screening', 'verified', 'reserved', 'allocated', 'monitored', 'suspended']
TRANSITIONS = {state: tuple(STATES[i + 1:i + 3]) for i, state in enumerate(STATES)}

@dataclass(frozen=True)
class TransitionPlan:
    from_state: str
    to_state: str
    allowed: bool
    reasons: tuple[str, ...]
    score: float

def allowed_targets(state: str) -> tuple[str, ...]:
    if state not in TRANSITIONS:
        raise ContractError('unknown workflow state')
    return TRANSITIONS[state]

def plan_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> TransitionPlan:
    context = context or {}
    if target not in STATES:
        raise ContractError('unknown target state')
    scorecard = record_score(record, context)
    reasons: list[str] = []
    structurally_allowed = target in allowed_targets(record.state)
    if not structurally_allowed:
        reasons.append('transition is not adjacent in the lifecycle')
    threshold = float(context.get('transition_threshold', 0.42))
    if scorecard['score'] < threshold:
        reasons.append('record score is below the transition threshold')
    return TransitionPlan(record.state, target, structurally_allowed and not reasons, tuple(reasons or ['eligible']), scorecard['score'])

def apply_transition(record: DomainRecord, target: str, context: Mapping[str, Any] | None = None) -> DomainRecord:
    plan = plan_transition(record, target, context)
    if not plan.allowed:
        raise ContractError('; '.join(plan.reasons))
    return record.with_state(target)

def guard_requestor_country_readiness_index_01(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_requestor_country_readiness_index_01_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_readiness_index_01' + (':passed' if allowed else ':blocked')

def guard_use_case_evidence_diversity_02(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_use_case_evidence_diversity_02_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_evidence_diversity_02' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_concentration_risk_03(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_public_value_proof_concentration_risk_03_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_concentration_risk_03' + (':passed' if allowed else ':blocked')

def guard_resource_gap_capacity_fit_04(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_resource_gap_capacity_fit_04_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_capacity_fit_04' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_commercial_resilience_05(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_partner_assurance_commercial_resilience_05_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_commercial_resilience_05' + (':passed' if allowed else ':blocked')

def guard_localization_effort_policy_exposure_06(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_localization_effort_policy_exposure_06_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_policy_exposure_06' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_dependency_fragility_07(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_delivery_capacity_dependency_fragility_07_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_dependency_fragility_07' + (':passed' if allowed else ':blocked')

def guard_requested_units_portfolio_value_08(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_requested_units_portfolio_value_08_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_portfolio_value_08' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_readiness_index_09(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_continuity_risk_readiness_index_09_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_readiness_index_09' + (':passed' if allowed else ':blocked')

def guard_policy_risk_evidence_diversity_10(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_policy_risk_evidence_diversity_10_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_evidence_diversity_10' + (':passed' if allowed else ':blocked')

def guard_operations_cost_concentration_risk_11(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_operations_cost_concentration_risk_11_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_concentration_risk_11' + (':passed' if allowed else ':blocked')

def guard_dependency_count_capacity_fit_12(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_dependency_count_capacity_fit_12_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_capacity_fit_12' + (':passed' if allowed else ':blocked')

def guard_requestor_country_commercial_resilience_13(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_requestor_country_commercial_resilience_13_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_commercial_resilience_13' + (':passed' if allowed else ':blocked')

def guard_use_case_policy_exposure_14(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_use_case_policy_exposure_14_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_policy_exposure_14' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_dependency_fragility_15(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_public_value_proof_dependency_fragility_15_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_dependency_fragility_15' + (':passed' if allowed else ':blocked')

def guard_resource_gap_portfolio_value_16(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_resource_gap_portfolio_value_16_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_portfolio_value_16' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_readiness_index_17(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_partner_assurance_readiness_index_17_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_readiness_index_17' + (':passed' if allowed else ':blocked')

def guard_localization_effort_evidence_diversity_18(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_localization_effort_evidence_diversity_18_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_evidence_diversity_18' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_concentration_risk_19(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_delivery_capacity_concentration_risk_19_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_concentration_risk_19' + (':passed' if allowed else ':blocked')

def guard_requested_units_capacity_fit_20(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_requested_units_capacity_fit_20_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_capacity_fit_20' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_commercial_resilience_21(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_continuity_risk_commercial_resilience_21_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_commercial_resilience_21' + (':passed' if allowed else ':blocked')

def guard_policy_risk_policy_exposure_22(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_policy_risk_policy_exposure_22_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_policy_exposure_22' + (':passed' if allowed else ':blocked')

def guard_operations_cost_dependency_fragility_23(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_operations_cost_dependency_fragility_23_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_dependency_fragility_23' + (':passed' if allowed else ':blocked')

def guard_dependency_count_portfolio_value_24(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_dependency_count_portfolio_value_24_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_portfolio_value_24' + (':passed' if allowed else ':blocked')

def guard_requestor_country_readiness_index_25(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_requestor_country_readiness_index_25_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_readiness_index_25' + (':passed' if allowed else ':blocked')

def guard_use_case_evidence_diversity_26(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_use_case_evidence_diversity_26_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_evidence_diversity_26' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_concentration_risk_27(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_public_value_proof_concentration_risk_27_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_concentration_risk_27' + (':passed' if allowed else ':blocked')

def guard_resource_gap_capacity_fit_28(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_resource_gap_capacity_fit_28_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_capacity_fit_28' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_commercial_resilience_29(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_partner_assurance_commercial_resilience_29_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_commercial_resilience_29' + (':passed' if allowed else ':blocked')

def guard_localization_effort_policy_exposure_30(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_localization_effort_policy_exposure_30_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_policy_exposure_30' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_dependency_fragility_31(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_delivery_capacity_dependency_fragility_31_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_dependency_fragility_31' + (':passed' if allowed else ':blocked')

def guard_requested_units_portfolio_value_32(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_requested_units_portfolio_value_32_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_portfolio_value_32' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_readiness_index_33(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_continuity_risk_readiness_index_33_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_readiness_index_33' + (':passed' if allowed else ':blocked')

def guard_policy_risk_evidence_diversity_34(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_policy_risk_evidence_diversity_34_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_evidence_diversity_34' + (':passed' if allowed else ':blocked')

def guard_operations_cost_concentration_risk_35(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_operations_cost_concentration_risk_35_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_concentration_risk_35' + (':passed' if allowed else ':blocked')

def guard_dependency_count_capacity_fit_36(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_dependency_count_capacity_fit_36_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_capacity_fit_36' + (':passed' if allowed else ':blocked')

def guard_requestor_country_commercial_resilience_37(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_requestor_country_commercial_resilience_37_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_commercial_resilience_37' + (':passed' if allowed else ':blocked')

def guard_use_case_policy_exposure_38(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_use_case_policy_exposure_38_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_policy_exposure_38' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_dependency_fragility_39(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_public_value_proof_dependency_fragility_39_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_dependency_fragility_39' + (':passed' if allowed else ':blocked')

def guard_resource_gap_portfolio_value_40(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_resource_gap_portfolio_value_40_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_portfolio_value_40' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_readiness_index_41(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_partner_assurance_readiness_index_41_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_readiness_index_41' + (':passed' if allowed else ':blocked')

def guard_localization_effort_evidence_diversity_42(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_localization_effort_evidence_diversity_42_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_evidence_diversity_42' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_concentration_risk_43(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_delivery_capacity_concentration_risk_43_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_concentration_risk_43' + (':passed' if allowed else ':blocked')

def guard_requested_units_capacity_fit_44(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_requested_units_capacity_fit_44_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_capacity_fit_44' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_commercial_resilience_45(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_continuity_risk_commercial_resilience_45_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_commercial_resilience_45' + (':passed' if allowed else ':blocked')

def guard_policy_risk_policy_exposure_46(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_policy_risk_policy_exposure_46_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_policy_exposure_46' + (':passed' if allowed else ':blocked')

def guard_operations_cost_dependency_fragility_47(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_operations_cost_dependency_fragility_47_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_dependency_fragility_47' + (':passed' if allowed else ':blocked')

def guard_dependency_count_portfolio_value_48(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_dependency_count_portfolio_value_48_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_portfolio_value_48' + (':passed' if allowed else ':blocked')

def guard_requestor_country_readiness_index_49(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_requestor_country_readiness_index_49_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_readiness_index_49' + (':passed' if allowed else ':blocked')

def guard_use_case_evidence_diversity_50(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_use_case_evidence_diversity_50_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_evidence_diversity_50' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_concentration_risk_51(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_public_value_proof_concentration_risk_51_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_concentration_risk_51' + (':passed' if allowed else ':blocked')

def guard_resource_gap_capacity_fit_52(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_resource_gap_capacity_fit_52_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_capacity_fit_52' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_commercial_resilience_53(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_partner_assurance_commercial_resilience_53_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_commercial_resilience_53' + (':passed' if allowed else ':blocked')

def guard_localization_effort_policy_exposure_54(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_localization_effort_policy_exposure_54_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_policy_exposure_54' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_dependency_fragility_55(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_delivery_capacity_dependency_fragility_55_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_dependency_fragility_55' + (':passed' if allowed else ':blocked')

def guard_requested_units_portfolio_value_56(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_requested_units_portfolio_value_56_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_portfolio_value_56' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_readiness_index_57(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_continuity_risk_readiness_index_57_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_readiness_index_57' + (':passed' if allowed else ':blocked')

def guard_policy_risk_evidence_diversity_58(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_policy_risk_evidence_diversity_58_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_evidence_diversity_58' + (':passed' if allowed else ':blocked')

def guard_operations_cost_concentration_risk_59(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_operations_cost_concentration_risk_59_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_concentration_risk_59' + (':passed' if allowed else ':blocked')

def guard_dependency_count_capacity_fit_60(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_dependency_count_capacity_fit_60_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_capacity_fit_60' + (':passed' if allowed else ':blocked')

def guard_requestor_country_commercial_resilience_61(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_requestor_country_commercial_resilience_61_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_commercial_resilience_61' + (':passed' if allowed else ':blocked')

def guard_use_case_policy_exposure_62(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_use_case_policy_exposure_62_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_policy_exposure_62' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_dependency_fragility_63(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_public_value_proof_dependency_fragility_63_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_dependency_fragility_63' + (':passed' if allowed else ':blocked')

def guard_resource_gap_portfolio_value_64(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_resource_gap_portfolio_value_64_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_portfolio_value_64' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_readiness_index_65(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_partner_assurance_readiness_index_65_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_readiness_index_65' + (':passed' if allowed else ':blocked')

def guard_localization_effort_evidence_diversity_66(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_localization_effort_evidence_diversity_66_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_evidence_diversity_66' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_concentration_risk_67(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_delivery_capacity_concentration_risk_67_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_concentration_risk_67' + (':passed' if allowed else ':blocked')

def guard_requested_units_capacity_fit_68(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_requested_units_capacity_fit_68_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_capacity_fit_68' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_commercial_resilience_69(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_continuity_risk_commercial_resilience_69_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_commercial_resilience_69' + (':passed' if allowed else ':blocked')

def guard_policy_risk_policy_exposure_70(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_policy_risk_policy_exposure_70_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_policy_exposure_70' + (':passed' if allowed else ':blocked')

def guard_operations_cost_dependency_fragility_71(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_operations_cost_dependency_fragility_71_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_dependency_fragility_71' + (':passed' if allowed else ':blocked')

def guard_dependency_count_portfolio_value_72(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_dependency_count_portfolio_value_72_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_portfolio_value_72' + (':passed' if allowed else ':blocked')

def guard_requestor_country_readiness_index_73(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_requestor_country_readiness_index_73_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_readiness_index_73' + (':passed' if allowed else ':blocked')

def guard_use_case_evidence_diversity_74(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_use_case_evidence_diversity_74_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_evidence_diversity_74' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_concentration_risk_75(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_public_value_proof_concentration_risk_75_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_concentration_risk_75' + (':passed' if allowed else ':blocked')

def guard_resource_gap_capacity_fit_76(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_resource_gap_capacity_fit_76_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_capacity_fit_76' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_commercial_resilience_77(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_partner_assurance_commercial_resilience_77_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_commercial_resilience_77' + (':passed' if allowed else ':blocked')

def guard_localization_effort_policy_exposure_78(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_localization_effort_policy_exposure_78_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_policy_exposure_78' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_dependency_fragility_79(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_delivery_capacity_dependency_fragility_79_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_dependency_fragility_79' + (':passed' if allowed else ':blocked')

def guard_requested_units_portfolio_value_80(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_requested_units_portfolio_value_80_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_portfolio_value_80' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_readiness_index_81(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_continuity_risk_readiness_index_81_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_readiness_index_81' + (':passed' if allowed else ':blocked')

def guard_policy_risk_evidence_diversity_82(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_policy_risk_evidence_diversity_82_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_evidence_diversity_82' + (':passed' if allowed else ':blocked')

def guard_operations_cost_concentration_risk_83(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_operations_cost_concentration_risk_83_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_concentration_risk_83' + (':passed' if allowed else ':blocked')

def guard_dependency_count_capacity_fit_84(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_dependency_count_capacity_fit_84_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_capacity_fit_84' + (':passed' if allowed else ':blocked')

def guard_requestor_country_commercial_resilience_85(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_requestor_country_commercial_resilience_85_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_commercial_resilience_85' + (':passed' if allowed else ':blocked')

def guard_use_case_policy_exposure_86(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_use_case_policy_exposure_86_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_policy_exposure_86' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_dependency_fragility_87(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_public_value_proof_dependency_fragility_87_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_dependency_fragility_87' + (':passed' if allowed else ':blocked')

def guard_resource_gap_portfolio_value_88(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_resource_gap_portfolio_value_88_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_portfolio_value_88' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_readiness_index_89(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_partner_assurance_readiness_index_89_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_readiness_index_89' + (':passed' if allowed else ':blocked')

def guard_localization_effort_evidence_diversity_90(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_localization_effort_evidence_diversity_90_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_evidence_diversity_90' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_concentration_risk_91(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_delivery_capacity_concentration_risk_91_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_concentration_risk_91' + (':passed' if allowed else ':blocked')

def guard_requested_units_capacity_fit_92(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_requested_units_capacity_fit_92_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_capacity_fit_92' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_commercial_resilience_93(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_continuity_risk_commercial_resilience_93_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_commercial_resilience_93' + (':passed' if allowed else ':blocked')

def guard_policy_risk_policy_exposure_94(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_policy_risk_policy_exposure_94_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_policy_exposure_94' + (':passed' if allowed else ':blocked')

def guard_operations_cost_dependency_fragility_95(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_operations_cost_dependency_fragility_95_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_dependency_fragility_95' + (':passed' if allowed else ':blocked')

def guard_dependency_count_portfolio_value_96(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_dependency_count_portfolio_value_96_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_portfolio_value_96' + (':passed' if allowed else ':blocked')

def guard_requestor_country_readiness_index_97(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_requestor_country_readiness_index_97_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_readiness_index_97' + (':passed' if allowed else ':blocked')

def guard_use_case_evidence_diversity_98(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_use_case_evidence_diversity_98_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_evidence_diversity_98' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_concentration_risk_99(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_public_value_proof_concentration_risk_99_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_concentration_risk_99' + (':passed' if allowed else ':blocked')

def guard_resource_gap_capacity_fit_100(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_resource_gap_capacity_fit_100_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_capacity_fit_100' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_commercial_resilience_101(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_partner_assurance_commercial_resilience_101_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_commercial_resilience_101' + (':passed' if allowed else ':blocked')

def guard_localization_effort_policy_exposure_102(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_localization_effort_policy_exposure_102_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_policy_exposure_102' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_dependency_fragility_103(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_delivery_capacity_dependency_fragility_103_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_dependency_fragility_103' + (':passed' if allowed else ':blocked')

def guard_requested_units_portfolio_value_104(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_requested_units_portfolio_value_104_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_portfolio_value_104' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_readiness_index_105(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_continuity_risk_readiness_index_105_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_readiness_index_105' + (':passed' if allowed else ':blocked')

def guard_policy_risk_evidence_diversity_106(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_policy_risk_evidence_diversity_106_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_evidence_diversity_106' + (':passed' if allowed else ':blocked')

def guard_operations_cost_concentration_risk_107(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_operations_cost_concentration_risk_107_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_concentration_risk_107' + (':passed' if allowed else ':blocked')

def guard_dependency_count_capacity_fit_108(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_dependency_count_capacity_fit_108_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_capacity_fit_108' + (':passed' if allowed else ':blocked')

def guard_requestor_country_commercial_resilience_109(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_requestor_country_commercial_resilience_109_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requestor_country_commercial_resilience_109' + (':passed' if allowed else ':blocked')

def guard_use_case_policy_exposure_110(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_use_case_policy_exposure_110_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_use_case_policy_exposure_110' + (':passed' if allowed else ':blocked')

def guard_public_value_proof_dependency_fragility_111(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_public_value_proof_dependency_fragility_111_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_public_value_proof_dependency_fragility_111' + (':passed' if allowed else ':blocked')

def guard_resource_gap_portfolio_value_112(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_resource_gap_portfolio_value_112_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_resource_gap_portfolio_value_112' + (':passed' if allowed else ':blocked')

def guard_partner_assurance_readiness_index_113(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('readiness_index', 0.0)
    floor = float(context.get('guard_partner_assurance_readiness_index_113_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_partner_assurance_readiness_index_113' + (':passed' if allowed else ':blocked')

def guard_localization_effort_evidence_diversity_114(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('evidence_diversity', 0.0)
    floor = float(context.get('guard_localization_effort_evidence_diversity_114_floor', 0.32))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_localization_effort_evidence_diversity_114' + (':passed' if allowed else ':blocked')

def guard_delivery_capacity_concentration_risk_115(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('concentration_risk', 0.0)
    floor = float(context.get('guard_delivery_capacity_concentration_risk_115_floor', 0.39))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_delivery_capacity_concentration_risk_115' + (':passed' if allowed else ':blocked')

def guard_requested_units_capacity_fit_116(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('capacity_fit', 0.0)
    floor = float(context.get('guard_requested_units_capacity_fit_116_floor', 0.46))
    state_ok = STATES.index(record.state) <= STATES.index('verified')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_requested_units_capacity_fit_116' + (':passed' if allowed else ':blocked')

def guard_continuity_risk_commercial_resilience_117(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('commercial_resilience', 0.0)
    floor = float(context.get('guard_continuity_risk_commercial_resilience_117_floor', 0.53))
    state_ok = STATES.index(record.state) <= STATES.index('reserved')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_continuity_risk_commercial_resilience_117' + (':passed' if allowed else ':blocked')

def guard_policy_risk_policy_exposure_118(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('policy_exposure', 0.0)
    floor = float(context.get('guard_policy_risk_policy_exposure_118_floor', 0.6000000000000001))
    state_ok = STATES.index(record.state) <= STATES.index('allocated')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_policy_risk_policy_exposure_118' + (':passed' if allowed else ':blocked')

def guard_operations_cost_dependency_fragility_119(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('dependency_fragility', 0.0)
    floor = float(context.get('guard_operations_cost_dependency_fragility_119_floor', 0.67))
    state_ok = STATES.index(record.state) <= STATES.index('monitored')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_operations_cost_dependency_fragility_119' + (':passed' if allowed else ':blocked')

def guard_dependency_count_portfolio_value_120(record: DomainRecord, context: Mapping[str, Any]) -> tuple[bool, str]:
    metrics = context.get('_metrics') or grouped_metrics(record, context)
    value = metrics.get('portfolio_value', 0.0)
    floor = float(context.get('guard_dependency_count_portfolio_value_120_floor', 0.25))
    state_ok = STATES.index(record.state) <= STATES.index('suspended')
    allowed = state_ok and value >= min(1.0, floor)
    return allowed, 'guard_dependency_count_portfolio_value_120' + (':passed' if allowed else ':blocked')

GUARDS: tuple[Callable[[DomainRecord, Mapping[str, Any]], tuple[bool, str]], ...] = (
    guard_requestor_country_readiness_index_01,
    guard_use_case_evidence_diversity_02,
    guard_public_value_proof_concentration_risk_03,
    guard_resource_gap_capacity_fit_04,
    guard_partner_assurance_commercial_resilience_05,
    guard_localization_effort_policy_exposure_06,
    guard_delivery_capacity_dependency_fragility_07,
    guard_requested_units_portfolio_value_08,
    guard_continuity_risk_readiness_index_09,
    guard_policy_risk_evidence_diversity_10,
    guard_operations_cost_concentration_risk_11,
    guard_dependency_count_capacity_fit_12,
    guard_requestor_country_commercial_resilience_13,
    guard_use_case_policy_exposure_14,
    guard_public_value_proof_dependency_fragility_15,
    guard_resource_gap_portfolio_value_16,
    guard_partner_assurance_readiness_index_17,
    guard_localization_effort_evidence_diversity_18,
    guard_delivery_capacity_concentration_risk_19,
    guard_requested_units_capacity_fit_20,
    guard_continuity_risk_commercial_resilience_21,
    guard_policy_risk_policy_exposure_22,
    guard_operations_cost_dependency_fragility_23,
    guard_dependency_count_portfolio_value_24,
    guard_requestor_country_readiness_index_25,
    guard_use_case_evidence_diversity_26,
    guard_public_value_proof_concentration_risk_27,
    guard_resource_gap_capacity_fit_28,
    guard_partner_assurance_commercial_resilience_29,
    guard_localization_effort_policy_exposure_30,
    guard_delivery_capacity_dependency_fragility_31,
    guard_requested_units_portfolio_value_32,
    guard_continuity_risk_readiness_index_33,
    guard_policy_risk_evidence_diversity_34,
    guard_operations_cost_concentration_risk_35,
    guard_dependency_count_capacity_fit_36,
    guard_requestor_country_commercial_resilience_37,
    guard_use_case_policy_exposure_38,
    guard_public_value_proof_dependency_fragility_39,
    guard_resource_gap_portfolio_value_40,
    guard_partner_assurance_readiness_index_41,
    guard_localization_effort_evidence_diversity_42,
    guard_delivery_capacity_concentration_risk_43,
    guard_requested_units_capacity_fit_44,
    guard_continuity_risk_commercial_resilience_45,
    guard_policy_risk_policy_exposure_46,
    guard_operations_cost_dependency_fragility_47,
    guard_dependency_count_portfolio_value_48,
    guard_requestor_country_readiness_index_49,
    guard_use_case_evidence_diversity_50,
    guard_public_value_proof_concentration_risk_51,
    guard_resource_gap_capacity_fit_52,
    guard_partner_assurance_commercial_resilience_53,
    guard_localization_effort_policy_exposure_54,
    guard_delivery_capacity_dependency_fragility_55,
    guard_requested_units_portfolio_value_56,
    guard_continuity_risk_readiness_index_57,
    guard_policy_risk_evidence_diversity_58,
    guard_operations_cost_concentration_risk_59,
    guard_dependency_count_capacity_fit_60,
    guard_requestor_country_commercial_resilience_61,
    guard_use_case_policy_exposure_62,
    guard_public_value_proof_dependency_fragility_63,
    guard_resource_gap_portfolio_value_64,
    guard_partner_assurance_readiness_index_65,
    guard_localization_effort_evidence_diversity_66,
    guard_delivery_capacity_concentration_risk_67,
    guard_requested_units_capacity_fit_68,
    guard_continuity_risk_commercial_resilience_69,
    guard_policy_risk_policy_exposure_70,
    guard_operations_cost_dependency_fragility_71,
    guard_dependency_count_portfolio_value_72,
    guard_requestor_country_readiness_index_73,
    guard_use_case_evidence_diversity_74,
    guard_public_value_proof_concentration_risk_75,
    guard_resource_gap_capacity_fit_76,
    guard_partner_assurance_commercial_resilience_77,
    guard_localization_effort_policy_exposure_78,
    guard_delivery_capacity_dependency_fragility_79,
    guard_requested_units_portfolio_value_80,
    guard_continuity_risk_readiness_index_81,
    guard_policy_risk_evidence_diversity_82,
    guard_operations_cost_concentration_risk_83,
    guard_dependency_count_capacity_fit_84,
    guard_requestor_country_commercial_resilience_85,
    guard_use_case_policy_exposure_86,
    guard_public_value_proof_dependency_fragility_87,
    guard_resource_gap_portfolio_value_88,
    guard_partner_assurance_readiness_index_89,
    guard_localization_effort_evidence_diversity_90,
    guard_delivery_capacity_concentration_risk_91,
    guard_requested_units_capacity_fit_92,
    guard_continuity_risk_commercial_resilience_93,
    guard_policy_risk_policy_exposure_94,
    guard_operations_cost_dependency_fragility_95,
    guard_dependency_count_portfolio_value_96,
    guard_requestor_country_readiness_index_97,
    guard_use_case_evidence_diversity_98,
    guard_public_value_proof_concentration_risk_99,
    guard_resource_gap_capacity_fit_100,
    guard_partner_assurance_commercial_resilience_101,
    guard_localization_effort_policy_exposure_102,
    guard_delivery_capacity_dependency_fragility_103,
    guard_requested_units_portfolio_value_104,
    guard_continuity_risk_readiness_index_105,
    guard_policy_risk_evidence_diversity_106,
    guard_operations_cost_concentration_risk_107,
    guard_dependency_count_capacity_fit_108,
    guard_requestor_country_commercial_resilience_109,
    guard_use_case_policy_exposure_110,
    guard_public_value_proof_dependency_fragility_111,
    guard_resource_gap_portfolio_value_112,
    guard_partner_assurance_readiness_index_113,
    guard_localization_effort_evidence_diversity_114,
    guard_delivery_capacity_concentration_risk_115,
    guard_requested_units_capacity_fit_116,
    guard_continuity_risk_commercial_resilience_117,
    guard_policy_risk_policy_exposure_118,
    guard_operations_cost_dependency_fragility_119,
    guard_dependency_count_portfolio_value_120,
)

def guard_report(record: DomainRecord, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    context = dict(context or {})
    context['_metrics'] = grouped_metrics(record, context)
    results = [guard(record, context) for guard in GUARDS]
    return {'passed': sum(item[0] for item in results), 'failed': sum(not item[0] for item in results),
            'messages': [item[1] for item in results]}

def decide(record: DomainRecord, context: Mapping[str, Any] | None = None) -> Decision:
    context = context or {}
    rules = evaluate(record, context)
    scorecard = record_score(record, context)
    guards = guard_report(record, context)
    effective_score = min(scorecard['score'], float(context.get('domain_signal', 1.0))) * (1.0 - max(0.0, float(context.get('allocation_concentration', 0.0)) - 0.5) * 0.4)
    critical = sum(item.severity == 'critical' for item in rules)
    if context.get('domain_severity') == 'critical':
        outcome = 'hold'
    elif critical:
        outcome = 'hold'
    elif effective_score >= float(context.get('approve_threshold', 0.62)) and guards['passed'] >= guards['failed']:
        outcome = 'approve'
    elif effective_score >= float(context.get('review_threshold', 0.38)):
        outcome = 'review'
    else:
        outcome = 'reject'
    reasons = (f"score={scorecard['score']:.6f}", f"critical={critical}",
               f"guards={guards['passed']}/{guards['passed'] + guards['failed']}")
    return Decision(record.record_id, outcome, effective_score, reasons, rules, scorecard['metrics'])

def advance_for_outcome(record: DomainRecord, decision: Decision) -> DomainRecord:
    current = STATES.index(record.state)
    if decision.outcome == 'approve' and current + 1 < len(STATES):
        return record.with_state(STATES[current + 1])
    if decision.outcome == 'hold' and STATES[-1] != record.state:
        return record.with_state(STATES[-1])
    return record
