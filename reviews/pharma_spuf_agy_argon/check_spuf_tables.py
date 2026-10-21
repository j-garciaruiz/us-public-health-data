import zipfile
import pandas as pd

with zipfile.ZipFile("data/raw/pharma/spuf/2026Q3/sample files PPUF_2026Q3.zip") as z:
    for name in z.namelist():
        print(f"=== {name} ===")
        with z.open(name) as f:
            for _ in range(5):
                line = f.readline().decode("latin1").strip()
                if line:
                    print(" ", line)
