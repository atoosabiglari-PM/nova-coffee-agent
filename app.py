from pathlib import Path

import pandas as pd
import streamlit as st

from approval import (
    get_all_approval_requests,
    review_approval_request,
    can_execute,
)


PROJECT_DIR = Path(__file__).resolve().parent
WORKBOOK = PROJECT_DIR / "NOVA_Coffee_Lab_Operations_2025_2026.xlsx"


st.set_page_config(
    page_title="NOVA Coffee Lab",
    page_icon="☕",
    layout="wide",
)


@st.cache_data
def load_workbook():
    return pd.read_excel(WORKBOOK, sheet_name=None)


data = load_workbook()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("☕ NOVA Coffee Lab")
st.subheader("AI Operations & Management Agent")

st.success("NOVA operational database connected successfully.")
st.write(f"Loaded **{len(data)} worksheets**.")


# ---------------------------------------------------------
# GOVERNANCE PRINCIPLE
# ---------------------------------------------------------

st.divider()

st.header("NOVA Governance")

st.info(
    'The agent proposes. Governance decides how much autonomy it receives.'
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Agent Role", "Analyze & Propose")

with col2:
    st.metric("Governance", "Deterministic")

with col3:
    st.metric("Protected Actions", "Human Approval")


# ---------------------------------------------------------
# HUMAN APPROVAL CENTER
# ---------------------------------------------------------

st.divider()

st.header("Human Approval Center")

st.write(
    "Protected NOVA actions remain blocked until a human explicitly "
    "approves them."
)

approval_requests = get_all_approval_requests()

if not approval_requests:
    st.info("No approval requests are currently available.")

else:
    for approval_id, request in approval_requests.items():

        st.subheader(f"Approval Request: {approval_id}")

        st.write(f"**Decision Area:** {request['decision_area']}")
        st.write(f"**Proposed Action:** {request['proposed_action']}")
        st.write(f"**Status:** `{request['status']}`")

        if request.get("human_decision"):
            st.write(
                f"**Human Decision:** `{request['human_decision']}`"
            )

        if request["status"] == "PENDING_HUMAN_APPROVAL":

            approve_col, reject_col = st.columns(2)

            with approve_col:
                if st.button(
                    "APPROVE",
                    key=f"approve_{approval_id}",
                    type="primary",
                ):
                    review_approval_request(
                        approval_id=approval_id,
                        human_decision="APPROVE",
                    )

                    st.rerun()

            with reject_col:
                if st.button(
                    "REJECT",
                    key=f"reject_{approval_id}",
                ):
                    review_approval_request(
                        approval_id=approval_id,
                        human_decision="REJECT",
                    )

                    st.rerun()

        permission = can_execute(approval_id)

        if permission.get("can_execute") is True:
            st.success(
                "Execution Gate: ELIGIBLE — explicit human approval "
                "has been recorded."
            )
        else:
            st.error(
                "Execution Gate: BLOCKED — explicit human approval "
                "has not been granted."
            )

        st.divider()


# ---------------------------------------------------------
# BUSINESS DATA
# ---------------------------------------------------------

st.header("Available Business Data")

for sheet_name, dataframe in data.items():

    # Evaluation ground truth is intentionally withheld
    # from the operational interface.
    if sheet_name == "Evaluation_GroundTruth":
        continue

    st.write(
        f"**{sheet_name}** — {len(dataframe):,} records"
    )