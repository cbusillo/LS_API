#!/usr/bin/env python
"""Kill then start front and back ends"""
import subprocess
import sys


def main():
    """Run front and backends until killed"""
    print(subprocess.run(["pkill", "-f", "flask"], check=False))
    print(subprocess.run(["pkill", "-f", "discord"], check=False))

    if "stop" in sys.argv:
        return

    subprocess.Popen("poetry run flask", shell=True)
    subprocess.Popen("poetry run discord", shell=True)


if __name__ == "__main__":
    main()
