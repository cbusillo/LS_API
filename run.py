#!/usr/bin/env python
"""Kill then start front and back ends"""
import subprocess
import sys


def main():
    """Run front and backends until killed"""
    print(subprocess.run(["pkill", "-f", "run_flask.py"], check=False))
    print(subprocess.run(["pkill", "-f", "run_discord.py"], check=False))

    if "stop" in sys.argv:
        return

    subprocess.Popen(f"{sys.executable} run_flask.py", shell=True)
    subprocess.Popen(f"{sys.executable} run_discord.py", shell=True)


if __name__ == "__main__":
    main()
