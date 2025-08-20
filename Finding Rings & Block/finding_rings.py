import pandas as pd
from rapidfuzz import process, fuzz
import os
import pandas as pd

import re

pattern = re.compile(
    r"""
    (?:
        r\d+                # r1, r12, etc
        (?:[-\s]*c[-\s]*\d+)?   # optional c1, c-1, c 1, etc
    )
    |
    (?:
        ring[-\s]*\d+        # ring1, ring-1, ring 1
        (?:[-\s]*c[-\s]*\d+)?   # optional c1 variations
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


def extract_tokens(text):
    ring_no = pattern.findall(text)
    return ring_no[0].upper().replace('RING', "R").replace("-", "").replace(" ", "").replace("C", "-C")


root_dir = "folder_data"  # your top directory

rows = []

for root, dirs, files in os.walk(root_dir):
    parts = root.split(os.sep)

    # Skip the root itself
    if len(parts) < 3:
        continue

    # Identify level2 (always index 1 from root_dir)
    level2 = parts[1]

    # If this is a "leaf" (no subdirs inside), record it
    if not dirs:
        last_level = parts[-1]
        mid_parts = parts[2:-1]  # everything between level2 and leaf
        mid_level = "|".join(mid_parts) if mid_parts else ""

        rows.append({
            "block_name": level2,
            "ring_name": extract_tokens(mid_level),
            "span_name": last_level.lower()
        })

df = pd.DataFrame(rows)
print(df)
# ---- 1. Load your Excel file ----
excel_path = "Video Data Migration_19.08.2025.xlsx"
sheet_name = "mp_surveyor_data"
df_excel = pd.read_excel(excel_path, sheet_name=sheet_name)

# ---- 2. Suppose your main DataFrame (from folder parsing) looks like this ----
# df_main = pd.DataFrame({"col1": [...], "col2": [...], "col3": [...]})

# ---- 3. Build a lookup list from df_main[col3] ----
choices = df["span_name"].astype(str).tolist()
choices.remove("old gp rout")

# ---- 4. Define fuzzy match function ----
def fuzzy_lookup(query, scorer=fuzz.WRatio, cutoff=88):
    if pd.isna(query):
        return None, None, None, 0
    match, score, idx = process.extractOne(
        str(query), choices, scorer=scorer, score_cutoff=cutoff,
    ) or (None, 0, None)

    if idx is not None:
        row = df.iloc[idx]
        return row["block_name"], row["ring_name"], row["span_name"], score
    return None, None, None, score


# ---- 5. Apply fuzzy matching on Excel column ----
lookup_column = "route_name"  # column name in Excel to match
df_excel[["block_name", "ring_name", "route_matched", "score"]] = df_excel[lookup_column].apply(
    lambda x: pd.Series(fuzzy_lookup(x.lower()))
)

# ---- 6. Save back to Excel with matches ----
output_path = "output_with_matches.xlsx"
df_excel.to_excel(output_path, index=False)

print("✅ Matching completed. Updated Excel saved at:", output_path)

