import zipfile
import pandas as pd
import time
import os

t0 = time.time()
scratch_dir = "/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch"
os.makedirs(scratch_dir, exist_ok=True)

mfp_df = pd.read_csv("data/raw/pharma/ira/selected_drugs_mfp.csv", dtype=str)
mfp_df["NDC11_clean"] = mfp_df["NDC-11"].str.replace("-", "", regex=False)
target_ndcs = set(mfp_df["NDC11_clean"].dropna().unique())
target_ndcs_bytes = {s.encode("ascii") for s in target_ndcs}
print(f"Total unique NDC-11 across all IPAYs in selected_drugs_mfp.csv: {len(target_ndcs)}")

rows_by_label = {}

for label in ["2025Q3", "2025Q4", "2026Q3"]:
    zpath = f"data/raw/pharma/spuf/{label}/pricing file PPUF_{label}.zip"
    matched = []
    n_lines = 0
    non_standard = 0
    t_start = time.time()
    with zipfile.ZipFile(zpath) as z:
        txt_name = z.namelist()[0]
        with z.open(txt_name) as f:
            header = f.readline().decode("ascii").strip().split("|")
            for raw_line in f:
                n_lines += 1
                if raw_line[13:14] == b"|" and raw_line[25:26] == b"|":
                    if raw_line[14:25] in target_ndcs_bytes:
                        matched.append(raw_line.decode("ascii").rstrip("\r\n").split("|"))
                else:
                    non_standard += 1
                    parts = raw_line.decode("ascii").rstrip("\r\n").split("|")
                    if parts[3] in target_ndcs:
                        matched.append(parts)
    df_match = pd.DataFrame(matched, columns=header)
    df_match["RELEASE"] = label
    rows_by_label[label] = df_match
    print(f"{label}: scanned {n_lines:,} lines (non_std={non_standard}) in {time.time() - t_start:.1f}s -> matched {len(df_match):,} rows")

all_matched = pd.concat(rows_by_label.values(), ignore_index=True)
out_path = os.path.join(scratch_dir, "spuf_matched_all_ndcs.csv")
all_matched.to_csv(out_path, index=False)
print(f"Saved {len(all_matched):,} matched rows to {out_path} in {time.time() - t0:.1f}s")
