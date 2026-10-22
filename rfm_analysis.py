
from datetime import datetime
from collections import defaultdict

# Demonstration data only — not real customer records
transactions = [
    ("C001", "2026-10-20", 2500),
    ("C001", "2026-10-15", 1800),
    ("C001", "2026-09-30", 3200),
    ("C002", "2026-08-10", 900),
    ("C003", "2026-10-18", 4500),
    ("C003", "2026-10-10", 2000),
    ("C004", "2026-05-01", 500),
    ("C005", "2026-10-21", 7000),
]

analysis_date = datetime(2026, 10, 23)
customers = defaultdict(list)

for customer_id, date, amount in transactions:
    purchase_date = datetime.strptime(date, "%Y-%m-%d")
    customers[customer_id].append((purchase_date, amount))

print("E-COMMERCE CUSTOMER SEGMENTATION")
print("-" * 65)

for customer_id, purchases in sorted(customers.items()):
    last_purchase = max(date for date, amount in purchases)

    recency = (analysis_date - last_purchase).days
    frequency = len(purchases)
    monetary = sum(amount for date, amount in purchases)

    if recency <= 30 and frequency >= 3:
        segment = "Loyal Customer"
    elif recency <= 30 and monetary >= 4000:
        segment = "High Value Customer"
    elif recency > 90:
        segment = "At Risk Customer"
    else:
        segment = "Regular Customer"

    print(f"Customer: {customer_id}")
    print(f"Recency: {recency} days")
    print(f"Frequency: {frequency} purchases")
    print(f"Monetary Value: INR {monetary}")
    print(f"Segment: {segment}")
    print("-" * 65)
