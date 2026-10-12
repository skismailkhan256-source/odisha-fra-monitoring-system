
import pandas as pd
from pathlib import Path


# Load the cleaned FRA dataset
file_path = Path("data/Cleaned/Odisha_FRA_Village_Master_Cleaned.csv")

if not file_path.exists():
    print("Dataset file not found:", file_path)
    raise SystemExit(1)

df = pd.read_csv(file_path, encoding="utf-8-sig")

# Fix column names before checking the data
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace("\ufeff", "", regex=False)
)

required_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village",
    "Beneficiary_Count"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("Required columns missing:", missing_columns)
    raise SystemExit(1)


print("\n========== DATASET OVERVIEW ==========")
print("File:", file_path)
print("Rows loaded:", len(df))
print("Columns:", len(df.columns))


# Find any repeated PDF headings left in the data
header_mask = (
    df["Block"].astype(str).str.strip().str.upper().eq("BLOCK")
    & df["Gram Panchayat"].astype(str).str.strip().str.upper().eq("GRAM PANCHAYAT")
    & df["Village"].astype(str).str.strip().str.upper().eq("VILLAGE")
)

print("\n========== HEADER CHECK ==========")
print("PDF header rows found:", int(header_mask.sum()))

# Ignore header artifacts for the checks below, without changing the file
checked_df = df.loc[~header_mask].copy()


# Check for exact duplicate rows
exact_duplicates = checked_df.duplicated().sum()

print("\n========== DUPLICATE CHECK ==========")
print("Exact duplicate rows:", int(exact_duplicates))

# Repeated locations need checking, but they are not removed automatically
location_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]

location_mask = checked_df.duplicated(
    subset=location_columns,
    keep=False
)

print("Rows with repeated village locations:", int(location_mask.sum()))

if location_mask.any():
    print("\nSample repeated locations:")
    print(
        checked_df.loc[
            location_mask,
            location_columns + ["Beneficiary_Count"]
        ].head(10).to_string(index=False)
    )


# Check missing values and blank text fields
print("\n========== MISSING VALUE CHECK ==========")

print(checked_df[required_columns].isnull().sum())

text_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]

for column in text_columns:
    blank_count = (
        checked_df[column]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )
    print(f"Blank {column} values:", int(blank_count))


# Check beneficiary counts
print("\n========== BENEFICIARY CHECK ==========")

beneficiary_count = pd.to_numeric(
    checked_df["Beneficiary_Count"],
    errors="coerce"
)

invalid_count = beneficiary_count.isna().sum()
zero_count = (beneficiary_count == 0).sum()
negative_count = (beneficiary_count < 0).sum()

print("Invalid beneficiary values:", int(invalid_count))
print("Zero beneficiary values:", int(zero_count))
print("Negative beneficiary values:", int(negative_count))

if beneficiary_count.notna().any():
    print("Minimum:", beneficiary_count.min())
    print("Maximum:", beneficiary_count.max())
    print("Average:", round(beneficiary_count.mean(), 2))
    print("Total beneficiaries:", int(beneficiary_count.sum()))
else:
    print("No valid beneficiary counts found.")


# Look for suspicious village labels
suspicious_names = [
    "TOTAL",
    "GRAND TOTAL",
    "SL. NO.",
    "VILLAGE",
    "NAME OF"
]

suspicious_mask = (
    checked_df["Village"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
    .isin(suspicious_names)
)

suspicious_df = checked_df.loc[suspicious_mask]

print("\n========== VILLAGE NAME CHECK ==========")
print("Suspicious village records:", len(suspicious_df))

if not suspicious_df.empty:
    print(suspicious_df.head(10).to_string(index=False))


# Check for common encoding issues in location names
bad_characters = ["Ã", "Â", "â", "ð", "�"]

print("\n========== ENCODING CHECK ==========")

for column in text_columns:
    issue_mask = checked_df[column].fillna("").astype(str).apply(
        lambda value: any(char in value for char in bad_characters)
    )

    print(f"{column} encoding issues:", int(issue_mask.sum()))


# Print the final summary
print("\n========== FINAL SUMMARY ==========")

print("Districts:", checked_df["District"].nunique())
print("Unique block names:", checked_df["Block"].nunique())
print("Unique Gram Panchayat names:", checked_df["Gram Panchayat"].nunique())
print("Unique village names:", checked_df["Village"].nunique())
print("Village records checked:", len(checked_df))
print("Missing cells:", int(checked_df[required_columns].isnull().sum().sum()))

print("\nQuality check completed.")
print("No changes were written to the dataset.")
