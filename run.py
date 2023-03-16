#!/usr/bin/env python

import subprocess
import sys


def main():
    print(subprocess.run(["pkill", "-f", "run_django.py"]))
    print(subprocess.run(["pkill", "-f", "run_discord.py"]))
    print(len(sys.argv))

    if "stop" in sys.argv:
        return

    subprocess.Popen(f"{sys.executable} run_django.py runserver", shell=True)
    subprocess.Popen(f"{sys.executable} run_discord.py", shell=True)


if __name__ == "__main__":
    main()
