# stepcast basic_pipeline.py — run with: python basic_pipeline.py
from stepcast import Pipeline

pipe = Pipeline("Hello World Pipeline")


@pipe.step("Say hello")
def say_hello() -> str:
    print("Hello from stepcast!")
    return "hello"


@pipe.step("Say goodbye")
def say_goodbye(greeting: str) -> str:
    print(f"Got: {greeting} — now saying goodbye!")
    return "goodbye"


@pipe.step("Report result")
def report(result: str) -> None:
    print(f"Pipeline finished with: {result}")


if __name__ == "__main__":
    report = pipe.run()
    print(f"\n{report.summary()}")
