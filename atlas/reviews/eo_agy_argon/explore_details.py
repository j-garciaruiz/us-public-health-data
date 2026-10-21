#!/usr/bin/env python3
"""Check data/raw contents and test variations in Task 1 and Task 2 specifications."""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

print("Files in data/raw:")
for p in sorted(RAW.rglob("*")):
    if p.is_file():
        print(" ", p.relative_to(RAW))
