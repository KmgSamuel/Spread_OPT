from __future__ import annotations
from typing import Dict
import pandas as pd
from .models import DealInput

# Helper normalization functions

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _marketplace_score(d: DealInput) -> float:
    # Positive contributors (0-10)
    pos = (
        d.fragmentation + d.frequency + d.take_rate_room + d.standardization +
        d.geographic_density + d.payment_flow
    ) / 6.0
    # Negative risks (0-10)
    neg = (d.regulatory_risk + d.leakage_risk + d.commoditization_risk + d.capital_intensity) / 4.0
    base = clamp(10 * (0.65 * pos/10 + 0.35 * (1 - neg/10)), 0, 10)
    return base


def _pricing_power_score(d: DealInput) -> float:
    # Gurley: pricing too high triggers disintermediation; consider sensitivity and room
    # Optimal take rate band influenced by category; proxy with rake_sensitivity and room
    # Start with room and inverse of sensitivity
    room = d.take_rate_room / 10
    sens = 1 - (d.rake_sensitivity / 10)
    # Penalty if take rate too high relative to sensitivity & value
    rate_norm = clamp(d.take_rate / 30.0, 0, 2)  # assume ~30% is very high for most
    penalty = max(0.0, rate_norm - (0.6 * room + 0.6 * sens))
    score = 10 * clamp(0.6 * room + 0.6 * sens - 0.8 * penalty, 0, 1)
    return score


def _network_effects_score(d: DealInput) -> float:
    # Network strength and routing power positive; disintermediation negative
    pos = (d.network_strength + d.routing_power) / 2
    neg = d.disintermediate_risk
    return clamp(0.75 * pos + 0.25 * (10 - neg), 0, 10)


def _unit_econ_score(d: DealInput) -> float:
    # Normalize CAC payback: 0 months = 10, 24 months = ~3, >36 = ~0
    if d.cac_payback_months <= 6:
        payback_score = 9.0
    elif d.cac_payback_months <= 12:
        payback_score = 8.0
    elif d.cac_payback_months <= 18:
        payback_score = 6.5
    elif d.cac_payback_months <= 24:
        payback_score = 5.0
    elif d.cac_payback_months <= 36:
        payback_score = 2.5
    else:
        payback_score = 0.5

    # LTV/CAC scaling: 1x=1, 3x=6, 5x=8, 10x=10
    ltv = d.ltv_cac
    if ltv <= 1:
        ltv_score = 1.0
    elif ltv <= 3:
        ltv_score = 6.0
    elif ltv <= 5:
        ltv_score = 8.0
    else:
        ltv_score = 10.0

    # Contribution margin mapping: -50%=1, 0%=4, 20%=7, 40%=9.5
    cm = d.contribution_margin
    if cm <= -20:
        cm_score = 1.0
    elif cm <= 0:
        cm_score = 4.0
    elif cm <= 20:
        cm_score = 7.0
    elif cm <= 40:
        cm_score = 9.0
    else:
        cm_score = 9.8

    return clamp(0.4 * payback_score + 0.35 * ltv_score + 0.25 * cm_score, 0, 10)


def _value_unlock_score(d: DealInput) -> float:
    # Proxy for "money out of nowhere" unlock vs status quo
    return clamp(float(d.value_unlock_index), 0, 10)


def _risk_adjustment(d: DealInput) -> float:
    # Convert risks into a deduction-based score (higher better)
    reg = d.regulatory_risk
    leak = d.leakage_risk
    commod = d.commoditization_risk
    dis = d.disintermediate_risk
    cap = d.capital_intensity
    raw = 10 - clamp(0.22*reg + 0.18*leak + 0.18*commod + 0.22*dis + 0.2*cap, 0, 10)
    return clamp(raw, 0, 10)


def score_deal_row(d: DealInput, weights: Dict[str, float]) -> Dict[str, float]:
    m = _marketplace_score(d)
    p = _pricing_power_score(d)
    n = _network_effects_score(d)
    u = _unit_econ_score(d)
    v = _value_unlock_score(d)
    r = _risk_adjustment(d)

    # Weighted sum scaled to 100
    wsum = (
        weights.get("marketplace",1)*m +
        weights.get("pricing_power",1)*p +
        weights.get("network_effects",1)*n +
        weights.get("unit_economics",1)*u +
        weights.get("value_unlock",1)*v +
        weights.get("risk",1)*r
    )
    wtotal = sum(weights.values()) if sum(weights.values())>0 else 1.0
    overall = 100.0 * (wsum / (wtotal * 10.0))

    return {
        "marketplace": round(m,2),
        "pricing_power": round(p,2),
        "network_effects": round(n,2),
        "unit_economics": round(u,2),
        "value_unlock": round(v,2),
        "risk_adj": round(r,2),
        "overall": round(overall,1),
    }


def aggregate_scores(df: pd.DataFrame, weights: Dict[str,float]) -> pd.DataFrame:
    # Expect all DealInput fields
    out = []
    for _, row in df.iterrows():
        d = DealInput(**row.to_dict())
        s = score_deal_row(d, weights)
        rec = {**row.to_dict(), **s}
        out.append(rec)
    return pd.DataFrame(out)
