from pydantic import BaseModel, Field
from typing import List

class DealInput(BaseModel):
    # Metadata
    name: str = Field(...)
    sector: str = Field(...)
    stage: str = Field(...)
    geo: str = Field(...)

    # Pricing / rake
    take_rate: float = Field(..., ge=0, le=90)
    rake_sensitivity: int = Field(..., ge=0, le=10)

    # Network & routing
    routing_power: int = Field(..., ge=0, le=10)
    network_strength: int = Field(..., ge=0, le=10)
    disintermediate_risk: int = Field(..., ge=0, le=10)

    # Marketplace 10-ish factors (proxies 0-10)
    fragmentation: int = Field(..., ge=0, le=10)
    frequency: int = Field(..., ge=0, le=10)
    take_rate_room: int = Field(..., ge=0, le=10)
    standardization: int = Field(..., ge=0, le=10)
    geographic_density: int = Field(..., ge=0, le=10)
    payment_flow: int = Field(..., ge=0, le=10)
    regulatory_risk: int = Field(..., ge=0, le=10)
    leakage_risk: int = Field(..., ge=0, le=10)
    commoditization_risk: int = Field(..., ge=0, le=10)
    capital_intensity: int = Field(..., ge=0, le=10)

    # Unit economics
    cac_payback_months: int = Field(..., ge=0, le=120)
    ltv_cac: float = Field(..., ge=0, le=50)
    contribution_margin: float = Field(..., ge=-100, le=100)

    # Value unlock
    value_unlock_index: int = Field(..., ge=0, le=10)


def factor_columns() -> List[str]:
    return [
        # metadata first
        "name","sector","stage","geo",
        # pricing & network
        "take_rate","rake_sensitivity","routing_power","network_strength","disintermediate_risk",
        # marketplace
        "fragmentation","frequency","take_rate_room","standardization","geographic_density","payment_flow",
        "regulatory_risk","leakage_risk","commoditization_risk","capital_intensity",
        # unit econ
        "cac_payback_months","ltv_cac","contribution_margin",
        # value unlock
        "value_unlock_index",
    ]


def required_columns() -> List[str]:
    # Same as factor_columns; CSV must include all
    return factor_columns()
