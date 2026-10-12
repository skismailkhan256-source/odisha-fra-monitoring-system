import pandas as pd

# Input files
village_file = "data/Cleaned/Odisha_FRA_Featured_Master.csv"
status_file = "data/Cleaned/Odisha_FRA_Implementation_Status.csv"

# Output file
output_file = "data/Cleaned/Odisha_FRA_District_Merged_Analysis.csv"


print("\nLoading FRA datasets...")

village_df = pd.read_csv(village_file)
status_df = pd.read_csv(status_file)


# Make district names similar
def district_key(name):

    name = str(name).strip().upper()

    district_names = {
        "ANGUL": "ANUGUL",
        "BALASORE": "BALESHWAR",
        "BHADRAKH": "BHADRAK",
        "BOLANGIR": "BALANGIR",
        "BOUDH": "BAUDH",
        "CUTTACKK": "CUTTACK",
        "DEOGARH": "DEBAGARH",
        "JAGATSINGHPUR": "JAGATSINGHAPUR",
        "JAJPUR": "JAJAPUR",
        "JHARUGUDA": "JHARSUGUDA",
        "KENDRAPADA": "KENDRAPARA",
        "KEONJHAR": "KENDUJHAR",
        "KHURDA": "KHORDHA"
    }

    return district_names.get(name, name)


# Create matching district key
village_df["District_Key"] = village_df["District"].apply(
    district_key
)

status_df["District_Key"] = status_df["District"].apply(
    district_key
)


# District-wise summary from village dataset
village_summary = village_df.groupby(
    "District_Key"
).agg(
    Total_Beneficiaries=("Beneficiary_Count", "sum"),
    Village_Records=("Village", "size"),
    Unique_Villages=("Village", "nunique"),
    Unique_Blocks=("Block", "nunique"),
    Unique_Gram_Panchayats=("Gram Panchayat", "nunique")
).reset_index()


# Merge implementation data with village summary
merged_df = pd.merge(
    status_df,
    village_summary,
    on="District_Key",
    how="left"
)


# Check whether village data is available
merged_df["Beneficiary_Data_Available"] = (
    merged_df["Total_Beneficiaries"]
    .notna()
    .map({
        True: "Yes",
        False: "No"
    })
)


# Remove helper column
merged_df = merged_df.drop(
    columns=["District_Key"]
)


# Save final dataset
merged_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)



print("FRA district merge completed successfully.")


print("Implementation districts:", len(status_df))
print("Final districts:", len(merged_df))
print("Final columns:", len(merged_df.columns))


print("\nBeneficiary data availability:")
print(
    merged_df["Beneficiary_Data_Available"].value_counts()
)


print("\nDistricts without village beneficiary data:")

missing = merged_df[
    merged_df["Beneficiary_Data_Available"] == "No"
]["District"]

print(missing.tolist())


print("\nFinal dataset saved at:")
print(output_file)