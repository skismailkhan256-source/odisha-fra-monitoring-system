
import pandas as pd
import unicodedata


# ==========================================
# 1. FILE PATHS
# ==========================================

input_file = "data/Cleaned/Odisha_FRA_Village_Master_Final.csv"

output_file = "data/Cleaned/Odisha_FRA_Village_Master_Cleaned.csv"


# ==========================================
# 2. LOAD MASTER DATASET
# ==========================================

df = pd.read_csv(input_file)

print("\nLoading master dataset...")
print("Rows before cleaning:", len(df))


# ==========================================
# 3. CLEAN COLUMN NAMES
# ==========================================

df.columns = (
    df.columns
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
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ==========================================
# 4. REMOVE EMPTY ROWS
# ==========================================

old_rows = len(df)

df = df.dropna(how="all").copy()

print("Empty rows removed:", old_rows - len(df))


# ==========================================
# 5. TEXT CLEANING
# ==========================================

def clean_text(value):

    if pd.isna(value):
        return value

    value = str(value)

    value = value.replace("\ufeff", "")
    value = value.replace("\u200b", "")
    value = value.replace("\xa0", " ")

    value = unicodedata.normalize("NFKC", value)

    value = " ".join(value.split())

    return value.strip()


# ==========================================
# 6. FIX ENCODING PROBLEMS
# ==========================================

def fix_encoding(value):

    if pd.isna(value):
        return value

    value = str(value)

    bad_chars = ["Ã", "Â", "â", "ð", "�"]

    if any(char in value for char in bad_chars):

        try:

            fixed = value.encode("latin1").decode("utf-8")

            if not any(char in fixed for char in bad_chars):
                return fixed

        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    return value


text_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]


for column in text_columns:

    df[column] = df[column].apply(clean_text)

    df[column] = df[column].apply(fix_encoding)

    df[column] = df[column].apply(clean_text)


# Standardize names

for column in text_columns:

    df[column] = df[column].str.upper()


# ==========================================
# 7. CLEAN BENEFICIARY COUNT
# ==========================================

df["Beneficiary_Count"] = pd.to_numeric(
    df["Beneficiary_Count"],
    errors="coerce"
)

invalid_values = df["Beneficiary_Count"].isna().sum()

negative_values = (
    df["Beneficiary_Count"] < 0
).sum()

print("\nInvalid beneficiary values:", invalid_values)

print("Negative beneficiary values:", negative_values)


df.loc[
    df["Beneficiary_Count"] < 0,
    "Beneficiary_Count"
] = pd.NA

# Remove rows with invalid beneficiary counts

before = len(df)

df = df.dropna(
    subset=["Beneficiary_Count"]
).copy()

print(
    "Rows removed due to invalid beneficiary counts:",
    before - len(df)
)

df["Beneficiary_Count"] = (
    df["Beneficiary_Count"].astype("Int64")
)


# ==========================================
# 8. REMOVE REPEATED PDF HEADER ROWS
# ==========================================

header_rows = (
    df["Block"].astype(str).str.strip().eq("BLOCK")
    |
    df["Gram Panchayat"]
    .astype(str).str.strip()
    .isin(["GRAM PANCHAYAT", "GRAM PANCHAYAT NAME"])
    |
    df["Village"].astype(str).str.strip().eq("VILLAGE")
)

print("\nPDF header rows found:", int(header_rows.sum()))

df = df.loc[~header_rows].copy()


# ==========================================
# 9. REMOVE PLACEHOLDER RECORDS
# ==========================================

def is_placeholder(value):

    if pd.isna(value):
        return True

    value = str(value).strip().upper()

    # Empty or missing values
    if value in ["", "NAN", "NONE", "NULL", "-", "NA"]:
        return True

    # PDF template placeholder text
    placeholder_phrases = [
        "NAME OF",
        "ENTER NAME",
        "BLOCK NAME",
        "VILLAGE NAME",
        "GRAM PANCHAYAT NAME",
        "PLACEHOLDER"
    ]

    if any(
        phrase in value
        for phrase in placeholder_phrases
    ):
        return True

    # Repeated PDF header / summary text
    invalid_values = [
        "BLOCK",
        "GRAM PANCHAYAT",
        "VILLAGE",
        "TOTAL",
        "GRAND TOTAL",
        "SL. NO.",
        "REJECTED"
    ]

    if value in invalid_values:
        return True

    return False


# Check required location columns

location_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]

placeholder_mask = pd.Series(
    False,
    index=df.index
)

for column in location_columns:

    placeholder_mask |= df[column].apply(is_placeholder)


# Display records before removal

placeholder_records = df.loc[
    placeholder_mask,
    location_columns + ["Beneficiary_Count"]
].copy()

print("\nPlaceholder records identified:")

print("Total:", len(placeholder_records))

if not placeholder_records.empty:

    print(
        placeholder_records.to_string(index=False)
    )


# Remove invalid location records

df = df.loc[~placeholder_mask].copy()

print(
    "\nPlaceholder records removed:",
    len(placeholder_records)
)


# ==========================================
# 10. REMOVE EXACT DUPLICATES
# ==========================================

before = len(df)

df = df.drop_duplicates().copy()

print(
    "\nExact duplicate rows removed:",
    before - len(df)
)


# ==========================================
# 11. CHECK REPEATED VILLAGE RECORDS
# ==========================================

location_columns = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village"
]

repeated = df.duplicated(
    subset=location_columns,
    keep=False
)

print(
    "Repeated village/location records:",
    int(repeated.sum())
)


# ==========================================
# 12. CHECK REMAINING ENCODING PROBLEMS
# ==========================================

bad_chars = ["Ã", "Â", "â", "ð", "�"]

for column in text_columns:

    bad_values = df[column].astype(str).apply(
        lambda value: any(
            char in value for char in bad_chars
        )
    )

    print(
        column,
        "encoding issues:",
        int(bad_values.sum())
    )


# ==========================================
# 13. FINAL DATASET INFORMATION
# ==========================================

print("\nFINAL CLEANED DATASET")
print("--------------------------------")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("Districts:", df["District"].nunique())

print("Blocks:", df["Block"].nunique())

print(
    "Gram Panchayats:",
    df["Gram Panchayat"].nunique()
)

print("Villages:", df["Village"].nunique())

print(
    "Total beneficiaries:",
    df["Beneficiary_Count"].sum()
)


# ==========================================
# 14. SAVE CLEANED DATASET
# ==========================================

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nCleaned dataset saved successfully.")

print(output_file)


# ==========================================
# 15. FINAL PLACEHOLDER VALIDATION
# ==========================================

remaining_placeholders = pd.Series(
    False,
    index=df.index
)

for column in location_columns:

    remaining_placeholders |= df[column].apply(
        is_placeholder
    )

print(
    "\nRemaining placeholder records:",
    int(remaining_placeholders.sum())
)

print("\nData cleaning completed successfully.")
