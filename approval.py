from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import json
import uuid


PROJECT_DIR = Path(__file__).resolve().parent
APPROVAL_STORE = PROJECT_DIR / "nova_approvals.json"


@dataclass
class ApprovalRequest:
    approval_id: str
    decision_area: str
    proposed_action: str
    status: str
    human_decision: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def _load_store() -> dict:
    if not APPROVAL_STORE.exists():
        return {}

    try:
        with open(APPROVAL_STORE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: dict) -> None:
    temp_file = APPROVAL_STORE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(store, file, indent=2, ensure_ascii=False)

    temp_file.replace(APPROVAL_STORE)


def create_approval_request(
    decision_area: str,
    proposed_action: str,
) -> dict:

    store = _load_store()

    approval_id = str(uuid.uuid4())[:8]

    request = ApprovalRequest(
        approval_id=approval_id,
        decision_area=decision_area,
        proposed_action=proposed_action,
        status="PENDING_HUMAN_APPROVAL",
        human_decision=None,
    )

    store[approval_id] = request.to_dict()
    _save_store(store)

    return request.to_dict()


def get_all_approval_requests() -> dict:
    return _load_store()


def get_approval_status(approval_id: str) -> dict:

    store = _load_store()
    request = store.get(approval_id)

    if request is None:
        return {
            "error": "Approval request not found.",
            "approval_id": approval_id,
        }

    return request


def review_approval_request(
    approval_id: str,
    human_decision: str,
) -> dict:

    store = _load_store()
    request = store.get(approval_id)

    if request is None:
        return {
            "error": "Approval request not found.",
            "approval_id": approval_id,
        }

    decision = human_decision.strip().upper()

    if decision not in {"APPROVE", "REJECT"}:
        return {
            "error": "Human decision must be APPROVE or REJECT.",
            "approval_id": approval_id,
            "status": request["status"],
        }

    request["human_decision"] = decision

    if decision == "APPROVE":
        request["status"] = "APPROVED"
    else:
        request["status"] = "REJECTED"

    store[approval_id] = request
    _save_store(store)

    return request


def can_execute(approval_id: str) -> dict:

    store = _load_store()
    request = store.get(approval_id)

    if request is None:
        return {
            "approval_id": approval_id,
            "can_execute": False,
            "reason": "Approval request not found.",
        }

    if request["status"] != "APPROVED":
        return {
            "approval_id": approval_id,
            "can_execute": False,
            "status": request["status"],
            "reason": "Explicit human approval has not been granted.",
        }

    return {
        "approval_id": approval_id,
        "can_execute": True,
        "status": request["status"],
        "reason": "Explicit human approval has been granted.",
    }