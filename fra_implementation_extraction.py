import pandas as pd
import pdfplumber

# PDF file
input_file = "data/raw/FRA_Implementation_Odisha_Sept_2025/FRA_Implementation_Status_Sep_2025.pdf"

# Output CSV
output_file = "data/Cleaned/Odisha_FRA_Implementation_Status.csv"


print("\nReading FRA implementation PDF...")

with pdfplumber.open(input_file) as pdf:

    # Page 1
    table1 = pdf.pages[0].extract_tables()[0]

    # Page 2
    table2 = pdf.pages[1].extract_tables()[0]


data = []


# Page 1 data
# Columns:
# 0 = Serial No.
# 1 = District
# 2 = District Code
# 3 = FRA Committees
# 8,9 = Total claims filed
# 14,15 = Total claims recommended by GS
# 20,21 = Total claims recommended by SDLC

for row in table1[4:]:

    if not row[0] or row[0] == "TOTAL":
        continue

    try:
        district = row[1]
        district_code = row[2]

        committees = int(row[3])

        claims_filed = int(row[8]) + int(row[9])

        claims_gs = int(row[14]) + int(row[15])

        claims_sdlc = int(row[20]) + int(row[21])

        data.append({
            "District": district,
            "District_Code": district_code,
            "FRA_Committees": committees,
            "Claims_Filed": claims_filed,
            "Claims_Recommended_GS_to_SDLC": claims_gs,
            "Claims_Recommended_SDLC_to_DLC": claims_sdlc
        })

    except (ValueError, TypeError):
        continue


# Page 2 data
# Columns:
# 6,7 = Approved total
# 12,13 = Titles distributed total
# 18,19 = Forest land total
# 24,25 = Rejected total

for i, row in enumerate(table2[4:]):

    if not row[0] or row[0] == "TOTAL":
        continue

    try:
        claims_approved = int(row[6]) + int(row[7])

        titles_distributed = int(row[12]) + int(row[13])

        forest_land = int(row[18]) + int(row[19])

        claims_rejected = int(row[24]) + int(row[25])

        data[i]["Claims_Approved"] = claims_approved
        data[i]["Titles_Distributed"] = titles_distributed
        data[i]["Forest_Land_Titles_Ha"] = forest_land
        data[i]["Claims_Rejected"] = claims_rejected

    except (ValueError, TypeError):
        continue


# Create dataframe
df = pd.DataFrame(data)


# Make number columns numeric
number_columns = [
    "District_Code",
    "FRA_Committees",
    "Claims_Filed",
    "Claims_Recommended_GS_to_SDLC",
    "Claims_Recommended_SDLC_to_DLC",
    "Claims_Approved",
    "Titles_Distributed",
    "Forest_Land_Titles_Ha",
    "Claims_Rejected"
]

for column in number_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Save CSV
df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


print("\nFRA implementation dataset created successfully.")
print("----------------------------------------")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nDistricts:")
print(df["District"].tolist())

print("\nTotal Claims Filed:", df["Claims_Filed"].sum())
print("Total Claims Approved:", df["Claims_Approved"].sum())
print("Total Titles Distributed:", df["Titles_Distributed"].sum())
print("Total Claims Rejected:", df["Claims_Rejected"].sum())

print("\nSaved at:")
print(output_file)