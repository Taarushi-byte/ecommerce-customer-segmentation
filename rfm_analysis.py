
import pandas as pd
from pathlib import Path

# Project configuration
DATA_FILE = Path("transactions.csv")
ANALYSIS_DATE = pd.Timestamp("2026-10-23")

def load_data(file_path):
    """Load and validate transaction data."""
    df = pd.read_csv(file_path)

    required = {"customer_id", "order_date", "amount"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain: {required}")

    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )
    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )

    df = df.dropna(
        subset=["customer_id", "order_date", "amount"]
    )

    if (df["amount"] < 0).any():
        raise ValueError("Transaction amounts cannot be negative.")

    if df.empty:
        raise ValueError("No valid transactions found.")

    return df

def calculate_rfm(df, analysis_date):
    """Calculate Recency, Frequency and Monetary value."""
    rfm = df.groupby("customer_id").agg(
        last_purchase=("order_date", "max"),
        frequency=("order_date", "count"),
        monetary=("amount", "sum")
    )

    rfm["recency"] = (
        analysis_date - rfm["last_purchase"]
    ).dt.days

    if (rfm["recency"] < 0).any():
        raise ValueError(
            "Transactions cannot occur after the analysis date."
        )

    # Score 1–5: 5 is best for all three metrics.
    # Lower recency is better, so reverse its ranking.
    rfm["R_score"] = pd.qcut(
        rfm["recency"].rank(method="first", ascending=False),
        5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["F_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["M_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"),
        5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["RFM_score"] = (
        rfm["R_score"].astype(str)
        + rfm["F_score"].astype(str)
        + rfm["M_score"].astype(str)
    )

    def segment(row):
        if row["R_score"] >= 4 and row["F_score"] >= 4:
            return "Loyal Customers"
        if row["R_score"] >= 4 and row["M_score"] >= 4:
            return "High Value Customers"
        if row["R_score"] <= 2:
            return "At Risk Customers"
        return "Regular Customers"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm.reset_index()

def main():
    transactions = load_data(DATA_FILE)
    rfm = calculate_rfm(transactions, ANALYSIS_DATE)

    output_file = "customer_segments.csv"
    rfm.to_csv(output_file, index=False)

    print("\nECOMMERCE CUSTOMER SEGMENTATION")
    print("=" * 50)
    print(f"Transactions analysed: {len(transactions)}")
    print(f"Customers analysed: {len(rfm)}")
    print("\nSegment summary:")
    print(rfm["segment"].value_counts().to_string())
    print(f"\nReport saved to {output_file}")

    print("\nCustomer report:")
    print(
        rfm[["customer_id", "recency", "frequency",
             "monetary", "RFM_score", "segment"]]
        .sort_values("monetary", ascending=False)
        .to_string(index=False)
    )

if __name__ == "__main__":
    main()

