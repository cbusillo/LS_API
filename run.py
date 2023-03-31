#!/usr/bin/env python
"""Kill then start front and back ends"""
import logging
import subprocess
import sys
import time


def main():
    """Run front and backends until killed with stop argument"""
    logging.info("Killing old processes")
    print(subprocess.run(["pkill", "-f", "discord"], check=False))
    print(subprocess.run(["pkill", "-f", "django"], check=False))
    print(subprocess.run(["pkill", "-f", "stunnel"], check=False))

    time.sleep(2)
    if "stop" in sys.argv:
        return
    logging.info("Starting new processes")
    subprocess.Popen("poetry run discord", shell=True)
    subprocess.Popen(
        "poetry run django",
        shell=True,
        stdin=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
