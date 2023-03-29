#!/usr/bin/env python
"""Kill then start front and back ends"""
import logging
import subprocess
import sys


def main():
    """Run front and backends until killed"""
    logging.info("Killing old processes")
    print(subprocess.run(["pkill", "-f", "django"], check=False))
    print(subprocess.run(["pkill", "-f", "discord"], check=False))

    if "stop" in sys.argv:
        return
    logging.info("Starting new processes")
    subprocess.Popen("/usr/local/bin/poetry run django", shell=True)
    subprocess.Popen("/usr/local/bin/poetry run discord", shell=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
