# stepcast api_client.py — HTTP steps with retry
# Requires: pip install stepcast requests
from stepcast import Pipeline

pipe = Pipeline("🌐 API Client Pipeline", fail_fast=False)


@pipe.step("Ping API health", retries=3, retry_delay=1.0, timeout=10)
def ping() -> dict:
    import urllib.request
    import json
    url = "https://httpbin.org/get"
    with urllib.request.urlopen(url, timeout=8) as resp:
        data = json.loads(resp.read())
    print(f"→ Status: 200 OK")
    print(f"→ Origin: {data.get('origin', 'unknown')}")
    return data


@pipe.step("Parse response")
def parse(data: dict) -> str:
    url = data.get("url", "unknown")
    print(f"→ Requested URL: {url}")
    return url


@pipe.step("Log result")
def log(url: str) -> None:
    print(f"→ Logging: {url}")
    print("→ Done!")


if __name__ == "__main__":
    report = pipe.run()
    print(f"\n{report.summary()}")
