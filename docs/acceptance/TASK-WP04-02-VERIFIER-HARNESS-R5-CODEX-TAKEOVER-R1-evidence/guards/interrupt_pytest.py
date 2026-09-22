#!/opt/homebrew/opt/python@3.12/bin/python3.12
"""Synthetic pytest replacement that interrupts its parent runner."""

import os
import signal
import time

os.kill(os.getppid(), signal.SIGINT)
time.sleep(1)
