import pandas as pd


# Load the cleaned FRA dataset
input_file = "data/Cleaned/Odisha_FRA_Village_Master_Cleaned.csv"
output_file = "data/Cleaned/Odisha_FRA_Featured_Master.csv"

df = pd.read_csv(input_file)

print("\nLoading cleaned dataset...")
print("Rows:", len(df))


# Make sure beneficiary values are numeric
df["Beneficiary_Count"] = pd.to_numeric(
    df["Beneficiary_Count"],
    errors="coerce"
)


# Total beneficiaries at Gram Panchayat level
df["GP_Total_Beneficiaries"] = (
    df.groupby(
        ["District", "Block", "Gram Panchayat"]
    )["Beneficiary_Count"]
    .transform("sum")
)


# Total beneficiaries at Block level
df["Block_Total_Beneficiaries"] = (
    df.groupby(
        ["District", "Block"]
    )["Beneficiary_Count"]
    .transform("sum")
)


# Total beneficiaries at District level
df["District_Total_Beneficiaries"] = (
    df.groupby(
        ["District"]
    )["Beneficiary_Count"]
    .transform("sum")
)


# Number of villages in each Gram Panchayat
df["GP_Village_Count"] = (
    df.groupby(
        ["District", "Block", "Gram Panchayat"]
    )["Village"]
    .transform("nunique")
)


# Number of villages in each Block
df["Block_Village_Count"] = (
    df.groupby(
        ["District", "Block"]
    )["Village"]
    .transform("nunique")
)


# Number of villages in each District
df["District_Village_Count"] = (
    df.groupby(
        ["District"]
    )["Village"]
    .transform("nunique")
)


# Village share within its Gram Panchayat
df["Village_Share_in_GP"] = (
    df["Beneficiary_Count"]
    / df["GP_Total_Beneficiaries"]
)


# Village share within its Block
df["Village_Share_in_Block"] = (
    df["Beneficiary_Count"]
    / df["Block_Total_Beneficiaries"]
)


# Village share within its District
df["Village_Share_in_District"] = (
    df["Beneficiary_Count"]
    / df["District_Total_Beneficiaries"]
)


# Create a simple beneficiary category
def beneficiary_category(value):
    if value <= 10:
        return "Low"
    elif value <= 50:
        return "Medium"
    else:
        return "High"


df["Beneficiary_Category"] = (
    df["Beneficiary_Count"]
    .apply(beneficiary_category)
)


# Save the feature dataset
df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


print("\nFeature engineering completed successfully.")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nNew features added:")
print("GP_Total_Beneficiaries")
print("Block_Total_Beneficiaries")
print("District_Total_Beneficiaries")
print("GP_Village_Count")
print("Block_Village_Count")
print("District_Village_Count")
print("Village_Share_in_GP")
print("Village_Share_in_Block")
print("Village_Share_in_District")
print("Beneficiary_Category")

print("\nFeatured dataset saved at:")
print(output_file)