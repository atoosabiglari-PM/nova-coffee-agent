from pathlib import Path
import pandas as pd


# Always locate the workbook inside the NOVA project folder,
# regardless of where ADK is launched from.
PROJECT_DIR = Path(__file__).resolve().parent
WORKBOOK = PROJECT_DIR / "NOVA_Coffee_Lab_Operations_2025_2026.xlsx"

# This sheet is intentionally excluded from agent-visible data.
HIDDEN_SHEETS = {"Evaluation_GroundTruth"}


def load_nova_data():
    """Load NOVA data while withholding evaluation ground truth."""
    all_data = pd.read_excel(WORKBOOK, sheet_name=None)

    return {
        sheet_name: df
        for sheet_name, df in all_data.items()
        if sheet_name not in HIDDEN_SHEETS
    }


def monthly_performance(data):
    """Prepare NOVA's monthly operating performance for analysis."""
    kpis = data["Monthly_KPIs"].copy()

    kpis["Month"] = pd.to_datetime(kpis["Month"])

    columns = [
        "Month",
        "Status",
        "Revenue",
        "Orders",
        "Units",
        "COGS",
        "Gross_Profit",
        "Gross_Margin",
        "Avg_Wait_Min",
        "Labor_Cost",
        "Labor_Hours",
        "Revenue/Labor_Hr",
        "MoM_Revenue_Growth",
        "YoY_Revenue_Growth",
        "Waste_Rate",
        "Stockouts",
    ]

    return kpis[columns].sort_values("Month")


if __name__ == "__main__":
    data = load_nova_data()
    performance = monthly_performance(data)

    print("\nNOVA COFFEE LAB — MONTHLY PERFORMANCE\n")
    print(performance.to_string(index=False))

    print("\nAgent-visible worksheets:")
    print(list(data.keys()))

    print("\nGround truth exposed to agent?")
    print("Evaluation_GroundTruth" in data)