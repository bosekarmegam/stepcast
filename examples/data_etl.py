# stepcast data_etl.py — copy and run with: python data_etl.py
# Requires: pip install stepcast
from stepcast import Pipeline
import os

pipe = Pipeline(
    "📊 Sales ETL",
    fail_fast=True,
    narrate=True,        # requires STEPCAST_GEMINI_API_KEY — silently skipped if absent
    dashboard=True,      # streams to localhost:4321 if stepcast serve is running
)


@pipe.step("📥 Download data", retries=3, retry_delay=2.0, timeout=30)
def download() -> str:
    import urllib.request
    # Simulate downloading — replace with real URL in production
    print("→ Simulating download of sales.csv")
    return "/tmp/stepcast_sample.csv"


@pipe.step("🧹 Clean & validate")
def clean(path: str) -> list[dict]:
    # Simulate CSV parsing
    rows = [
        {"order_id": "1001", "amount": "250.00"},
        {"order_id": "1002", "amount": "125.50"},
        {"order_id": "1003", "amount": "89.99"},
    ]
    valid = [r for r in rows if r.get("order_id") and float(r.get("amount", 0)) > 0]
    print(f"→ {len(valid)} valid rows retained")
    return valid


@pipe.step("📊 Aggregate KPIs")
def aggregate(rows: list) -> dict:
    total = sum(float(r["amount"]) for r in rows)
    avg = total / len(rows) if rows else 0
    print(f"→ Total: ${total:,.2f}  |  Avg: ${avg:.2f}  |  Count: {len(rows)}")
    return {"total": total, "avg": avg, "count": len(rows)}


@pipe.step(
    "📧 Send report",
    skip_if=lambda: os.getenv("SKIP_EMAIL") == "1",
    timeout=15,
)
def send_email(data: dict) -> None:
    print(f"→ Sending to team@example.com")
    print(f"→ Report: {data}")
    print("→ Email sent ✓")


if __name__ == "__main__":
    report = pipe.run()
    report.to_file("runs/latest.json")
    print(f"\n{report.summary()}")
