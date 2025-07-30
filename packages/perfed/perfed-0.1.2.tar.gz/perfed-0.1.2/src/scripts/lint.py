import subprocess


def start() -> None:
    print("Starting lint with ruff:")
    print("------------------------------------------------------------")
    ruff_process = subprocess.Popen(["ruff", "check", "./src", "--config", "./pyproject.toml"])
    ruff_exit_code = ruff_process.wait()
    exit(ruff_exit_code)
