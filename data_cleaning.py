import pandas as pd
import unicodedata


input_file = "data/Cleaned/Odisha_FRA_Village_Master_Final.csv"
output_file = "data/Cleaned/Odisha_FRA_Village_Master_Cleaned.csv"


# Load the master dataset
df = pd.read_csv(input_file)

print("\nLoading master dataset...")
print("Rows before cleaning:", len(df))


# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.replace("\ufeff", "", regex=False)
)


# Remove completely empty rows
old_rows = len(df)

df = df.dropna(how="all").copy()

print("Empty rows removed:", old_rows - len(df))


# Clean text values
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


# Fix common encoding problems
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


# Apply text cleaning
for column in text_columns:
    df[column] = df[column].apply(clean_text)
    df[column] = df[column].apply(fix_encoding)
    df[column] = df[column].apply(clean_text)


# Keep names in a consistent format
for column in text_columns:
    df[column] = df[column].str.upper()


# Clean beneficiary count
df["Beneficiary_Count"] = pd.to_numeric(
    df["Beneficiary_Count"],
    errors="coerce"
)

negative_values = (df["Beneficiary_Count"] < 0).sum()

print("\nInvalid beneficiary values:",
      df["Beneficiary_Count"].isna().sum())

print("Negative beneficiary values:",
      negative_values)

df.loc[
    df["Beneficiary_Count"] < 0,
    "Beneficiary_Count"
] = pd.NA

df["Beneficiary_Count"] = df["Beneficiary_Count"].astype("Int64")


# Remove repeated PDF header rows
header_rows = (
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

print("\nPDF header rows found:", header_rows.sum())

df = df[~header_rows].copy()


# Remove exact duplicate rows
before = len(df)

df = df.drop_duplicates().copy()

print("Exact duplicates removed:", before - len(df))


# Check repeated village records
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

print("Repeated village/location records:", repeated.sum())


# Check suspicious village names
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
    .str.strip()
    .str.upper()
    .isin(suspicious_words)
]

print("Suspicious village records:", len(suspicious))


# Check remaining encoding problems
bad_chars = ["Ã", "Â", "â", "ð", "�"]

for column in text_columns:
    bad_values = df[column].astype(str).apply(
        lambda x: any(char in x for char in bad_chars)
    )

    print(
        column,
        "encoding issues:",
        bad_values.sum()
    )


# Final information
print("\nFinal dataset")
print("------------------------------")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Districts:", df["District"].nunique())
print("Blocks:", df["Block"].nunique())
print("Gram Panchayats:", df["Gram Panchayat"].nunique())
print("Villages:", df["Village"].nunique())
print("Total beneficiaries:",
      df["Beneficiary_Count"].sum())


# Save cleaned dataset
df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nCleaned dataset saved successfully.")
print(output_file)

bad_chars = ["Ã", "Â", "â", "ð", "�"]

bad_village = df[
    df["Village"].astype(str).apply(
        lambda x: any(char in x for char in bad_chars)
    )
]

print("\nVillage with encoding issue:")
print(bad_village.to_string(index=False))