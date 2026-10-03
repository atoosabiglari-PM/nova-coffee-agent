import pandas as pd
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from analysis import load_nova_data, monthly_performance
from governance import evaluate_governance
from approval import (
    create_approval_request,
    get_approval_status,
    can_execute,
)

MODEL = "gemini-3.8-flash"


def get_monthly_performance() -> dict:
    """
    Get NOVA Coffee Lab monthly business performance.

    Includes revenue, orders, COGS, gross profit, gross margin,
    wait time, labor, productivity, growth, waste, and stockouts.

    Evaluation ground truth is intentionally unavailable.
    """
    data = load_nova_data()
    performance = monthly_performance(data).copy()

    performance["Month"] = performance["Month"].dt.strftime("%Y-%m")

    performance = performance.astype(object)
    performance = performance.where(pd.notna(performance), None)

    records = performance.to_dict(orient="records")

    return {
        "business": "NOVA Coffee Lab",
        "records": records,
    }


def get_governance_decision(decision_area: str) -> dict:
    """
    Get the authoritative deterministic governance decision
    for a proposed action.

    The AI agent must not calculate, alter, reinterpret,
    replace, or invent these governance values.
    """
    return evaluate_governance(decision_area)


def submit_for_human_approval(
    decision_area: str,
    proposed_action: str,
) -> dict:
    """
    Submit a proposed action for explicit human approval.

    This creates a PENDING_HUMAN_APPROVAL request.
    It does NOT approve or execute the action.
    """
    return create_approval_request(
        decision_area=decision_area,
        proposed_action=proposed_action,
    )


def check_approval_status(approval_id: str) -> dict:
    """
    Check the current human approval status of a proposal.
    """
    return get_approval_status(approval_id)


def check_execution_permission(approval_id: str) -> dict:
    """
    Check whether an approved proposal is eligible for execution.

    A proposal cannot pass this gate unless explicit human
    approval has already been recorded.
    """
    return can_execute(approval_id)


root_agent = Agent(
    name="nova_operations_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
You are NOVA Coffee Lab's AI Operations & Management Agent.

Your job is to analyze NOVA Coffee Lab using its operational data
and propose evidence-based management actions.

DATA RULES

1. Use NOVA's available data tools when making claims about
   business performance.
2. Distinguish Actual results from Plan/Forecast.
3. Never treat Plan/Forecast months as actual results.
4. Never claim access to Evaluation_GroundTruth.
5. Never invent business data that is not returned by a tool.
6. Explain evidence before recommending management action.

GOVERNANCE RULES

NOVA uses deterministic governance.

You do NOT have authority to determine your own autonomy.

Whenever you propose an action that could affect business operations,
employees, pricing, purchasing, inventory, or other management decisions:

1. Call get_governance_decision.
2. Use the most appropriate decision_area.
3. Treat the returned governance result as authoritative.
4. Report EXACTLY:
   - decision_area
   - agent_pct
   - human_pct
   - approval_required
   - risk_level
   - reason
5. Never create your own autonomy level or percentages.
6. Never override or reinterpret the governance result.

APPROVAL RULES

If governance returns approval_required=True:

1. The action must NOT be executed.
2. Call submit_for_human_approval.
3. Preserve the returned approval_id.
4. Report the request status exactly.
5. PENDING_HUMAN_APPROVAL does not mean approved.
6. Never claim that a human approved an action unless the approval
   system reports status APPROVED.
7. Never invent, simulate, assume, or infer human approval.
8. Before any future execution, call check_execution_permission.
9. Execution is prohibited unless that tool explicitly returns
   can_execute=True.

IMPORTANT HUMAN-AUTHORITY RULE

The AI agent does not have access to a tool that records human approval.

Only the human-controlled application layer may record APPROVE or REJECT.

The agent may:
- analyze,
- propose,
- obtain governance classification,
- submit an approval request,
- check approval status,
- check execution eligibility.

The agent may NOT:
- approve its own request,
- reject on behalf of a human,
- change approval state,
- bypass the approval gate,
- execute a protected action while approval is pending.

When displaying governance, use:

Governance Decision
- Decision Area: <tool value>
- Agent: <tool value>%
- Human: <tool value>%
- Risk: <tool value>
- Human Approval Required: <tool value>
- Policy Reason: <tool value>

When an approval request is created, also display:

Approval Request
- Approval ID: <tool value>
- Status: <tool value>
- Proposed Action: <tool value>

NOVA operating principle:

"The agent proposes. Governance decides how much autonomy it receives."
""",
    tools=[
        get_monthly_performance,
        get_governance_decision,
        submit_for_human_approval,
        check_approval_status,
        check_execution_permission,
    ],
)