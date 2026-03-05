# stepcast ai_pipeline.py — Gemini narration example
# Requires: pip install 'stepcast[gemini]'
# Set STEPCAST_GEMINI_API_KEY env var to enable narration
from stepcast import Pipeline

pipe = Pipeline(
    "🤖 AI-Narrated Pipeline",
    narrate=True,    # silently disabled if STEPCAST_GEMINI_API_KEY is not set
)


@pipe.step("Load config")
def load_config() -> dict:
    config = {"env": "production", "version": "1.2.3", "workers": 4}
    print(f"→ Loaded config: {config}")
    return config


@pipe.step("Validate config")
def validate(config: dict) -> dict:
    required = ["env", "version", "workers"]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    print(f"→ All {len(required)} required keys present")
    return config


@pipe.step("Deploy")
def deploy(config: dict) -> str:
    env = config["env"]
    version = config["version"]
    print(f"→ Deploying version {version} to {env}...")
    print("→ Deploy complete!")
    return f"deployed-{version}"


@pipe.step("Notify team")
def notify(deployment_id: str) -> None:
    print(f"→ Sending Slack notification for {deployment_id}")
    print("→ Team notified!")


if __name__ == "__main__":
    report = pipe.run()
    print(f"\n{report.summary()}")
    for step in report.steps:
        if step.narration:
            print(f"\n  [{step.label}] 💬 {step.narration}")
