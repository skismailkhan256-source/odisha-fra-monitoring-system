import pandas as pd


# ============================================================
# LOAD MASTER DATASET
# ============================================================

file_path = "data/Cleaned/Odisha_FRA_Village_Master.csv"

df = pd.read_csv(file_path)

print("\n========== BEFORE CLEANING ==========")
print("Total rows:", len(df))


# ============================================================
# REMOVE OBVIOUS PDF HEADER ARTIFACTS
# ============================================================

header_mask = (
    df["Block"].astype(str).str.strip().str.upper().eq("BLOCK")
    &
    df["Gram Panchayat"]
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("GRAM PANCHAYAT")
    &
    df["Village"]
    .astype(str)
    .str.strip()
    .str.upper()
    .eq("VILLAGE")
)

removed_headers = header_mask.sum()

print("Header artifact rows found:", removed_headers)

df = df[~header_mask].copy()


# ============================================================
# CHECK DUPLICATES
# ============================================================

duplicate_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]

duplicates = df.duplicated(
    subset=duplicate_columns,
    keep=False
)

print("Duplicate village records:", duplicates.sum())


# ============================================================
# CHECK MISSING VALUES
# ============================================================

print("\n========== MISSING VALUE CHECK ==========")

print(df.isnull().sum())


# ============================================================
# CHECK SUSPICIOUS VILLAGE NAMES
# ============================================================

suspicious_words = [
    "TOTAL",
    "GRAND TOTAL",
    "SL. NO.",
    "VILLAGE",
    "NAME OF"
]

suspicious = df[
    df["Village"]
    .astype(str)
    .str.upper()
    .str.strip()
    .isin(suspicious_words)
]

print("\n========== SUSPICIOUS VILLAGE CHECK ==========")

print("Suspicious records:", len(suspicious))

if len(suspicious) > 0:
    print("\nRecords requiring inspection:")
    print(suspicious.to_string(index=False))


# ============================================================
# BENEFICIARY COUNT CHECK
# ============================================================

print("\n========== BENEFICIARY COUNT CHECK ==========")

print("Minimum:", df["Beneficiary_Count"].min())
print("Maximum:", df["Beneficiary_Count"].max())
print("Average:", round(df["Beneficiary_Count"].mean(), 2))

invalid_count = (
    df["Beneficiary_Count"] <= 0
).sum()

print("Zero/negative records:", invalid_count)


# ============================================================
# SAVE CLEANED MASTER DATASET
# ============================================================

df.to_csv(
    file_path,
    index=False
)

print("\n========== CLEANING COMPLETED ==========")

print("Removed header artifacts:", removed_headers)
print("Final rows:", len(df))

print(
    "\nCleaned master dataset saved successfully."
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n========== FINAL SUMMARY ==========")

print("Districts:", df["District"].nunique())
print("Village records:", len(df))
print(
    "Missing values:",
    df.isnull().sum().sum()
)
print(
    "Duplicate records:",
    df.duplicated(
        subset=duplicate_columns
    ).sum()
)

print("\n========== DONE ==========\n")