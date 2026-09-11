# ============================================================
# ODISHA FRA MONITORING SYSTEM
# AUTOMATIC PDF CLEANING + VILLAGE SUMMARY + MERGING
# ============================================================


# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

import os
import re
import pdfplumber
import pandas as pd


# ============================================================
# 2. DATA FOLDER PATHS
# ============================================================

RAW_DATA_PATH = "data/raw"
CLEANED_DATA_PATH = "data/Cleaned"

os.makedirs(CLEANED_DATA_PATH, exist_ok=True)


print("\n==============================================")
print("      ODISHA FRA DATA PROCESSING SYSTEM")
print("==============================================")



# ============================================================
# 3. FIND ALL DISTRICT FOLDERS
# ============================================================

districts = [
    folder
    for folder in os.listdir(RAW_DATA_PATH)
    if os.path.isdir(
        os.path.join(RAW_DATA_PATH, folder)
    )
]

districts = sorted(districts)

print("\nDistrict folders found:")
print(districts)

print("\nTotal district folders:", len(districts))



# ============================================================
# 4. BASIC TEXT CLEANING
# ============================================================

def clean_text(value):

    # Handle missing values

    if value is None or pd.isna(value):
        return ""

    # Convert value into string

    value = str(value)

    # Replace line breaks with spaces

    value = value.replace("\n", " ")

    # Remove multiple spaces

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Remove leading and trailing spaces

    return value.strip()



# ============================================================
# 5. SAFE OCR DUPLICATION FIX
# ============================================================

def fix_doubled_text(text):

    # Handle missing values safely

    if text is None or pd.isna(text):
        return ""

    text = str(text).strip()

    # Empty text

    if text == "":
        return ""

    # Detect full character duplication
    #
    # Example:
    # NNiisshhcchhiinnttaa
    #
    # becomes:
    # Nishchintaa

    if len(text) % 2 == 0:

        first_half_pattern = text[::2]
        second_half_pattern = text[1::2]

        if first_half_pattern == second_half_pattern:

            return first_half_pattern

    return text



# ============================================================
# 6. CHECK WHETHER VALUE IS A "DO" PLACEHOLDER
# ============================================================

def is_do_value(value):

    if value is None or pd.isna(value):
        return True

    value = str(value).strip()

    if value == "":
        return True

    # Remove spaces and hyphens for checking

    normalized = re.sub(
        r"[\s\-]+",
        "",
        value.lower()
    )

    # Detect:
    # -do-
    # --do--
    # -- ddoo --
    # etc.

    if re.fullmatch(
        r"d+o+",
        normalized
    ):

        return True

    return False



# ============================================================
# 7. EXTRACT TABLES FROM PDF
# ============================================================

def extract_pdf_tables(pdf_path):

    all_rows = []

    print("\n----------------------------------------------")
    print("Reading PDF:")
    print(pdf_path)
    print("----------------------------------------------")

    try:

        with pdfplumber.open(pdf_path) as pdf:

            total_pages = len(pdf.pages)

            print(
                "Total pages:",
                total_pages
            )

            for page_number, page in enumerate(
                pdf.pages,
                start=1
            ):

                try:

                    table = page.extract_table()

                    if table:

                        for row in table:

                            # Keep only rows having data

                            if row and len(row) >= 5:

                                # Keep first five columns

                                all_rows.append(
                                    row[:5]
                                )

                    # Progress message

                    if page_number % 100 == 0:

                        print(
                            f"Processed "
                            f"{page_number}/"
                            f"{total_pages} pages"
                        )

                except Exception as page_error:

                    print(
                        f"Warning: Page "
                        f"{page_number} skipped."
                    )

                    print(
                        "Reason:",
                        page_error
                    )

    except Exception as pdf_error:

        print(
            "\nERROR reading PDF:"
        )

        print(pdf_error)

        return pd.DataFrame()


    return pd.DataFrame(
        all_rows
    )



# ============================================================
# 8. CLEAN FRA DATA
# ============================================================

def clean_fra_data(
    df,
    district_name
):

    # Check whether dataframe is empty

    if df.empty:

        return pd.DataFrame(
            columns=[
                "Sl. No.",
                "Block",
                "Gram Panchayat",
                "Village",
                "Name of the FRA beneficiary",
                "District"
            ]
        )


    # Make a copy

    df = df.copy()


    # Make sure only first five columns are used

    df = df.iloc[:, :5].copy()


    # Give standard column names

    df.columns = [
        "Sl. No.",
        "Block",
        "Gram Panchayat",
        "Village",
        "Name of the FRA beneficiary"
    ]


    # Clean text in every column

    for column in df.columns:

        df[column] = df[column].apply(
            clean_text
        )


    # --------------------------------------------------------
    # REMOVE REPEATED HEADERS
    # --------------------------------------------------------

    df = df[
        ~df["Sl. No."].str.contains(
            "Sl. No.",
            case=False,
            na=False
        )
    ].copy()


    # --------------------------------------------------------
    # REMOVE 1 2 3 4 5 HEADER NUMBERING ROW
    # --------------------------------------------------------

    df = df[
        ~(
            (df["Sl. No."] == "1") &
            (df["Block"] == "2") &
            (df["Gram Panchayat"] == "3") &
            (df["Village"] == "4") &
            (
                df[
                    "Name of the FRA beneficiary"
                ] == "5"
            )
        )
    ].copy()


    # --------------------------------------------------------
    # CONVERT -DO- VALUES TO EMPTY
    # --------------------------------------------------------

    for column in [
        "Block",
        "Gram Panchayat",
        "Village"
    ]:

        df[column] = df[column].apply(
            lambda x: ""
            if is_do_value(x)
            else x
        )


    # --------------------------------------------------------
    # FORWARD FILL LOCATION
    # --------------------------------------------------------

    location_columns = [
        "Block",
        "Gram Panchayat",
        "Village"
    ]

    df[location_columns] = (
        df[location_columns]
        .replace("", pd.NA)
        .ffill()
        .fillna("")
    )


    # --------------------------------------------------------
    # FIX OCR DUPLICATION
    # --------------------------------------------------------

    for column in location_columns:

        df[column] = df[column].apply(
            fix_doubled_text
        )


    # --------------------------------------------------------
    # CLEAN LOCATION TEXT AGAIN
    # --------------------------------------------------------

    for column in location_columns:

        df[column] = df[column].apply(
            clean_text
        )


    # --------------------------------------------------------
    # STANDARDIZE CASE
    #
    # This only changes upper/lowercase.
    # It does NOT guess spelling corrections.
    # --------------------------------------------------------

    for column in location_columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.upper()
        )


    # --------------------------------------------------------
    # REMOVE ROWS WITHOUT BENEFICIARY NAME
    # --------------------------------------------------------

    df = df[
        df[
            "Name of the FRA beneficiary"
        ]
        .astype(str)
        .str.strip()
        .ne("")
    ].copy()


    # --------------------------------------------------------
    # REMOVE OBVIOUS NUMERIC GARBAGE LOCATION ROWS
    # Example:
    # Block = 2
    # GP = 4
    # Village = 5
    # --------------------------------------------------------

    numeric_location_mask = (
        df["Block"]
        .astype(str)
        .str.fullmatch(r"\d+")
        &
        df["Gram Panchayat"]
        .astype(str)
        .str.fullmatch(r"\d+")
        &
        df["Village"]
        .astype(str)
        .str.fullmatch(r"\d+")
    )

    df = df[
        ~numeric_location_mask
    ].copy()


    # --------------------------------------------------------
    # ADD DISTRICT
    # --------------------------------------------------------

    df["District"] = district_name


    # Reset row numbers

    df = df.reset_index(
        drop=True
    )


    return df



# ============================================================
# 9. CREATE VILLAGE-LEVEL SUMMARY
# ============================================================

def create_village_summary(
    clean_df
):

    # Group beneficiary records by location

    village_summary = (
        clean_df
        .groupby(
            [
                "District",
                "Block",
                "Gram Panchayat",
                "Village"
            ],
            as_index=False
        )
        .size()
        .rename(
            columns={
                "size":
                "Beneficiary_Count"
            }
        )
    )


    return village_summary



# ============================================================
# 10. PROCESS ALL DISTRICTS
# ============================================================

all_village_summaries = []

successful_districts = []

failed_districts = []


for district in districts:

    print("\n")
    print("==============================================")
    print(
        "PROCESSING DISTRICT:",
        district
    )
    print("==============================================")


    # Create district cleaned folder

    district_clean_path = os.path.join(
        CLEANED_DATA_PATH,
        district
    )

    os.makedirs(
        district_clean_path,
        exist_ok=True
    )


    # Output village summary

    village_summary_path = os.path.join(
        district_clean_path,
        f"{district}_Village_Summary.csv"
    )


    # --------------------------------------------------------
    # IF SUMMARY ALREADY EXISTS
    # --------------------------------------------------------

    if os.path.exists(
        village_summary_path
    ):

        print(
            "\nExisting village summary found."
        )

        print(
            "Loading saved CSV..."
        )

        try:

            village_summary = pd.read_csv(
                village_summary_path
            )


            # Check required columns

            required_columns = [
                "District",
                "Block",
                "Gram Panchayat",
                "Village",
                "Beneficiary_Count"
            ]


            if all(
                column in village_summary.columns
                for column in required_columns
            ):

                print(
                    "Loaded villages:",
                    len(village_summary)
                )

                all_village_summaries.append(
                    village_summary
                )

                successful_districts.append(
                    district
                )

                continue

            else:

                print(
                    "Saved CSV structure is invalid."
                )

                print(
                    "Reprocessing district..."
                )

        except Exception as csv_error:

            print(
                "Could not load saved CSV."
            )

            print(
                csv_error
            )

            print(
                "Reprocessing district..."
            )


    # --------------------------------------------------------
    # FIND DISTRICT PDF FILES
    # --------------------------------------------------------

    district_path = os.path.join(
        RAW_DATA_PATH,
        district
    )


    pdf_files = [
        file
        for file in os.listdir(
            district_path
        )
        if file.lower().endswith(".pdf")
    ]


    pdf_files = sorted(
        pdf_files
    )


    print(
        "\nPDF files found:",
        len(pdf_files)
    )


    if not pdf_files:

        print(
            "WARNING: No PDF found for",
            district
        )

        failed_districts.append(
            district
        )

        continue


    # --------------------------------------------------------
    # PROCESS ALL PDFs IN THIS DISTRICT
    # --------------------------------------------------------

    district_dataframes = []


    for pdf_number, pdf_file in enumerate(
        pdf_files,
        start=1
    ):

        print("\n")
        print(
            f"PDF {pdf_number}/"
            f"{len(pdf_files)}:"
        )

        print(pdf_file)


        pdf_path = os.path.join(
            district_path,
            pdf_file
        )


        # Extract PDF

        raw_df = extract_pdf_tables(
            pdf_path
        )


        print(
            "Raw extracted rows:",
            len(raw_df)
        )


        if raw_df.empty:

            print(
                "WARNING: No data extracted."
            )

            continue


        # Clean PDF data

        clean_df = clean_fra_data(
            raw_df,
            district
        )


        print(
            "Cleaned rows:",
            len(clean_df)
        )


        if not clean_df.empty:

            district_dataframes.append(
                clean_df
            )


    # --------------------------------------------------------
    # CHECK WHETHER DISTRICT DATA EXISTS
    # --------------------------------------------------------

    if not district_dataframes:

        print(
            "\nNo usable data found for:",
            district
        )

        failed_districts.append(
            district
        )

        continue


    # --------------------------------------------------------
    # MERGE ALL PDFs OF THE DISTRICT
    # --------------------------------------------------------

    combined_clean_df = pd.concat(
        district_dataframes,
        ignore_index=True
    )


    print(
        "\nCombined cleaned beneficiary records:",
        len(combined_clean_df)
    )


    # --------------------------------------------------------
    # CREATE VILLAGE SUMMARY
    # --------------------------------------------------------

    village_summary = create_village_summary(
        combined_clean_df
    )


    # --------------------------------------------------------
    # REMOVE EXACT DUPLICATES
    # --------------------------------------------------------

    village_summary = (
        village_summary
        .drop_duplicates(
            subset=[
                "District",
                "Block",
                "Gram Panchayat",
                "Village"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # SAVE DISTRICT SUMMARY
    # --------------------------------------------------------

    village_summary.to_csv(
        village_summary_path,
        index=False
    )


    print(
        "\nVillage summary saved:"
    )

    print(
        village_summary_path
    )


    print(
        "Total villages:",
        len(village_summary)
    )


    # Add to master list

    all_village_summaries.append(
        village_summary
    )


    successful_districts.append(
        district
    )



# ============================================================
# 11. CREATE MASTER ODISHA DATASET
# ============================================================

print("\n")
print("==============================================")
print("CREATING ODISHA MASTER DATASET")
print("==============================================")


if all_village_summaries:

    # Combine all district summaries

    odisha_master_df = pd.concat(
        all_village_summaries,
        ignore_index=True
    )


    # Remove exact duplicate village records

    odisha_master_df = (
        odisha_master_df
        .drop_duplicates(
            subset=[
                "District",
                "Block",
                "Gram Panchayat",
                "Village"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # SAVE MASTER DATASET
    # --------------------------------------------------------

    master_path = os.path.join(
        CLEANED_DATA_PATH,
        "Odisha_FRA_Village_Master.csv"
    )


    odisha_master_df.to_csv(
        master_path,
        index=False
    )


    print(
        "\nOdisha master dataset saved!"
    )

    print(
        "File:",
        master_path
    )

    print(
        "Total village records:",
        len(odisha_master_df)
    )


    # --------------------------------------------------------
    # MASTER DATASET VALIDATION
    # --------------------------------------------------------

    print("\n")
    print("MASTER DATASET CHECK")
    print("----------------------------------------------")


    print(
        "Districts in master:",
        odisha_master_df[
            "District"
        ].nunique()
    )


    print(
        "Total villages:",
        len(odisha_master_df)
    )


    print(
        "Missing District:",
        odisha_master_df[
            "District"
        ].isna().sum()
    )


    print(
        "Missing Block:",
        odisha_master_df[
            "Block"
        ].isna().sum()
    )


    print(
        "Missing Gram Panchayat:",
        odisha_master_df[
            "Gram Panchayat"
        ].isna().sum()
    )


    print(
        "Missing Village:",
        odisha_master_df[
            "Village"
        ].isna().sum()
    )


    print(
        "Missing Beneficiary Count:",
        odisha_master_df[
            "Beneficiary_Count"
        ].isna().sum()
    )


    print("\nFirst 10 master records:")

    print(
        odisha_master_df.head(10)
    )


else:

    print(
        "\nNo district data was successfully processed."
    )



# ============================================================
# 12. PROCESSING SUMMARY
# ============================================================

print("\n")
print("==============================================")
print("PROCESSING SUMMARY")
print("==============================================")


print(
    "District folders found:",
    len(districts)
)


print(
    "Successfully processed:",
    len(successful_districts)
)


print(
    "Failed / no usable data:",
    len(failed_districts)
)


print(
    "\nSuccessful districts:"
)

print(
    successful_districts
)


if failed_districts:

    print(
        "\nFailed districts:"
    )

    print(
        failed_districts
    )


# ============================================================
# 13. COMPLETED
# ============================================================

print("\n")
print("==============================================")
print("      PIPELINE COMPLETED SUCCESSFULLY")
print("==============================================")