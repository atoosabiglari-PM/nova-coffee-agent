from dataclasses import dataclass, asdict


@dataclass
class GovernanceDecision:
    decision_area: str
    agent_pct: int
    human_pct: int
    approval_required: bool
    risk_level: str
    reason: str

    def to_dict(self):
        return asdict(self)


# Canonical NOVA governance policies.
GOVERNANCE_RULES = {
    "analysis": {
        "agent_pct": 90,
        "human_pct": 10,
        "approval_required": False,
        "risk_level": "Low",
        "reason": "Analysis is read-only and does not change business operations.",
    },

    "inventory_analysis": {
        "agent_pct": 85,
        "human_pct": 15,
        "approval_required": False,
        "risk_level": "Low",
        "reason": "Inventory analysis is read-only and reversible.",
    },

    "pricing_recommendation": {
        "agent_pct": 60,
        "human_pct": 40,
        "approval_required": True,
        "risk_level": "Medium",
        "reason": "Pricing affects customers, revenue, and margin.",
    },

    "inventory_purchase": {
        "agent_pct": 40,
        "human_pct": 60,
        "approval_required": True,
        "risk_level": "High",
        "reason": "Purchasing creates a financial commitment.",
    },

    "staffing_change": {
        "agent_pct": 30,
        "human_pct": 70,
        "approval_required": True,
        "risk_level": "High",
        "reason": "Staffing changes affect employees, labor cost, and operations.",
    },

    "employee_action": {
        "agent_pct": 10,
        "human_pct": 90,
        "approval_required": True,
        "risk_level": "Critical",
        "reason": "Employee-impacting actions require strong human oversight.",
    },
}


# Common model/user wording is mapped to the canonical policy.
GOVERNANCE_ALIASES = {
    # Analysis
    "business_analysis": "analysis",
    "performance_analysis": "analysis",
    "operational_analysis": "analysis",

    # Inventory analysis
    "inventory": "inventory_analysis",
    "inventory_review": "inventory_analysis",
    "stock_analysis": "inventory_analysis",

    # Pricing
    "pricing": "pricing_recommendation",
    "price_change": "pricing_recommendation",
    "pricing_change": "pricing_recommendation",
    "price_recommendation": "pricing_recommendation",

    # Purchasing
    "purchase": "inventory_purchase",
    "purchasing": "inventory_purchase",
    "procurement": "inventory_purchase",
    "inventory_order": "inventory_purchase",
    "supplier_order": "inventory_purchase",

    # Staffing
    "staffing": "staffing_change",
    "schedule_change": "staffing_change",
    "staff_schedule": "staffing_change",
    "shift_change": "staffing_change",
    "scheduling": "staffing_change",
    "labor_schedule": "staffing_change",

    # Employee actions
    "employee": "employee_action",
    "employee_change": "employee_action",
    "personnel_action": "employee_action",
    "disciplinary_action": "employee_action",
}


def normalize_decision_area(decision_area: str) -> str:
    """
    Normalize model/user wording into a canonical NOVA governance category.
    """

    normalized = decision_area.strip().lower()

    normalized = normalized.replace("-", "_")
    normalized = normalized.replace("/", "_")
    normalized = normalized.replace(" ", "_")

    while "__" in normalized:
        normalized = normalized.replace("__", "_")

    return GOVERNANCE_ALIASES.get(normalized, normalized)


def evaluate_governance(decision_area: str) -> dict:
    """
    Determine how much autonomy NOVA receives for a proposed action.

    Governance values are deterministic policy values.
    Gemini does not choose its own autonomy level.

    Known aliases are normalized to canonical policy categories.
    Unknown actions fail safely toward human control.
    """

    canonical_area = normalize_decision_area(decision_area)

    rule = GOVERNANCE_RULES.get(canonical_area)

    if rule is None:
        rule = {
            "agent_pct": 20,
            "human_pct": 80,
            "approval_required": True,
            "risk_level": "High",
            "reason": (
                "This action is not yet classified by NOVA's governance policy, "
                "so it defaults to human approval."
            ),
        }

    decision = GovernanceDecision(
        decision_area=canonical_area,
        agent_pct=rule["agent_pct"],
        human_pct=rule["human_pct"],
        approval_required=rule["approval_required"],
        risk_level=rule["risk_level"],
        reason=rule["reason"],
    )

    return decision.to_dict()


if __name__ == "__main__":
    test_cases = [
        "analysis",
        "business analysis",
        "inventory",
        "pricing",
        "purchase",
        "staffing",
        "staffing_change",
        "schedule change",
        "employee action",
        "unknown action",
    ]

    for case in test_cases:
        print(f"\nINPUT: {case}")
        print(evaluate_governance(case))