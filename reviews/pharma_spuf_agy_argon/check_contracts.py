import pandas as pd

df30 = pd.read_pickle("/Users/hari/.gemini/antigravity-cli/brain/b77c3068-2413-430a-92fa-36da5abcebb0/scratch/spuf_matched_30d.pkl")
for rel, grp in df30.groupby("RELEASE"):
    print(rel, "CONTRACT_ID first char counts (rows):", grp["CONTRACT_ID"].str[0].value_counts().to_dict())
    print(rel, "CONTRACT_ID first char counts (unique contracts):", grp.drop_duplicates("CONTRACT_ID")["CONTRACT_ID"].str[0].value_counts().to_dict())
    print(rel, "CONTRACT_ID first char counts (unique plan_seg):", grp.drop_duplicates(["CONTRACT_ID", "PLAN_ID", "SEGMENT_ID"])["CONTRACT_ID"].str[0].value_counts().to_dict())
