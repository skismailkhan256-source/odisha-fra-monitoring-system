# ============================================================
# ODISHA FRA MONITORING SYSTEM
# AUTOMATIC DATA CLEANING + DISTRICT MERGING PIPELINE
# ============================================================

import os
import re
import pdfplumber
import pandas as pd


# ============================================================
# 1. PATHS
# ============================================================

RAW_DATA_PATH = "data/raw"
CLEANED_DATA_PATH = "data/Cleaned"

os.makedirs(CLEANED_DATA_PATH, exist_ok=True)


# ============================================================
# 2. STANDARD COLUMNS
# ============================================================

RAW_COLUMNS = [
    "Sl. No.",
    "Block",
    "Gram Panchayat",
    "Village",
    "Name of the FRA beneficiary"
]

SUMMARY_COLUMNS = [
    "District",
    "Block",
    "Gram Panchayat",
    "Village",
    "Beneficiary_Count"
]


# ============================================================
# 3. BASIC TEXT CLEANING
# ============================================================

def clean_text(value):

    if value is None or pd.isna(value):
        return ""

    value = str(value)

    value = value.replace("\n", " ")

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# 4. SAFE OCR DOUBLE CHARACTER FIX
# ============================================================

def fix_doubled_text(value):

    if value is None or pd.isna(value):
        return ""

    value = str(value).strip()

    if value == "":
        return ""

    # Only fix a string when EVERY character is duplicated.
    #
    # Example:
    # NNiisshhcchhiinnttaa
    # ->
    # Nishchintaa

    if len(value) >= 4 and len(value) % 2 == 0:

        first = value[::2]
        second = value[1::2]

        if first == second:
            return first

    return value


# ============================================================
# 5. CHECK -DO- VALUE
# ============================================================

def is_do_value(value):

    if value is None or pd.isna(value):
        return True

    value = str(value).strip().lower()

    if value == "":
        return True

    normalized = re.sub(
        r"[\s\-]+",
        "",
        value
    )

    return normalized == "do"


# ============================================================
# 6. REMOVE OBVIOUS HEADER ARTIFACTS
# ============================================================

def remove_header_artifacts(df):

    # Case 1:
    # BLOCK | GRAM PANCHAYAT | VILLAGE

    mask_1 = (
        df["Block"]
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("BLOCK")
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

    # Case 2:
    # GRAM PANCHAYAT | VILLAGE
    #
    # Some PDFs have a damaged/missing Block header.

    mask_2 = (
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

    header_mask = mask_1 | mask_2

    removed = int(header_mask.sum())

    if removed > 0:

        print(
            f"Header artifact rows removed: {removed}"
        )

    return df.loc[
        ~header_mask
    ].copy()


# ============================================================
# 7. EXTRACT ALL TABLES FROM A PDF
# ============================================================

def extract_pdf_tables(pdf_path):

    all_rows = []

    print("\n----------------------------------------------")
    print(
        "Reading:",
        os.path.basename(pdf_path)
    )
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

                            if row:

                                row = list(row[:5])

                                while len(row) < 5:
                                    row.append("")

                                all_rows.append(row)

                except Exception as page_error:

                    print(
                        f"Warning: page {page_number} "
                        f"could not be extracted."
                    )

                if page_number % 100 == 0:

                    print(
                        f"Processed "
                        f"{page_number}/{total_pages} pages"
                    )

    except Exception as error:

        print(
            "PDF ERROR:",
            error
        )

        return pd.DataFrame(
            columns=RAW_COLUMNS
        )

    df = pd.DataFrame(
        all_rows,
        columns=RAW_COLUMNS
    )

    print(
        "Raw extracted rows:",
        len(df)
    )

    return df


# ============================================================
# 8. CLEAN RAW BENEFICIARY DATA
# ============================================================

def clean_fra_data(
    df,
    district_name
):

    if df.empty:

        return pd.DataFrame(
            columns=SUMMARY_COLUMNS
        )

    df = df.copy()

    # Keep first 5 columns only

    df = df.iloc[:, :5]

    df.columns = RAW_COLUMNS

    # --------------------------------------------------------
    # Basic text cleaning
    # --------------------------------------------------------

    for column in RAW_COLUMNS:

        df[column] = (
            df[column]
            .apply(clean_text)
        )

    # --------------------------------------------------------
    # Remove repeated headers
    # --------------------------------------------------------

    df = df[
        ~df["Sl. No."]
        .str.upper()
        .str.contains(
            "SL. NO.",
            na=False
        )
    ].copy()

    # --------------------------------------------------------
    # Remove 1 2 3 4 5 numbering row
    # --------------------------------------------------------

    numbering_mask = (
        df["Sl. No."].eq("1")
        &
        df["Block"].eq("2")
        &
        df["Gram Panchayat"].eq("3")
        &
        df["Village"].eq("4")
        &
        df[
            "Name of the FRA beneficiary"
        ].eq("5")
    )

    df = df[
        ~numbering_mask
    ].copy()

    # --------------------------------------------------------
    # Convert -do- to blank
    # --------------------------------------------------------

    location_columns = [
        "Block",
        "Gram Panchayat",
        "Village"
    ]

    for column in location_columns:

        df[column] = df[column].apply(
            lambda x:
            ""
            if is_do_value(x)
            else x
        )

    # --------------------------------------------------------
    # Forward fill locations
    # --------------------------------------------------------

    df[location_columns] = (
        df[location_columns]
        .replace("", pd.NA)
        .ffill()
        .fillna("")
    )

    # --------------------------------------------------------
    # Fix OCR duplication in locations
    # --------------------------------------------------------

    for column in location_columns:

        df[column] = (
            df[column]
            .apply(fix_doubled_text)
        )

    # --------------------------------------------------------
    # Clean again
    # --------------------------------------------------------

    for column in location_columns:

        df[column] = (
            df[column]
            .apply(clean_text)
        )

    # --------------------------------------------------------
    # Remove rows without beneficiary
    # --------------------------------------------------------

    beneficiary_column = (
        "Name of the FRA beneficiary"
    )

    df[beneficiary_column] = (
        df[beneficiary_column]
        .fillna("")
        .astype(str)
        .apply(clean_text)
    )

    df = df[
        df[beneficiary_column]
        .str.strip()
        .ne("")
    ].copy()

    # --------------------------------------------------------
    # Remove obvious numeric garbage rows
    # --------------------------------------------------------

    numeric_location_mask = (
        df["Block"]
        .astype(str)
        .str.fullmatch(
            r"\d+",
            na=False
        )
        &
        df["Gram Panchayat"]
        .astype(str)
        .str.fullmatch(
            r"\d+",
            na=False
        )
        &
        df["Village"]
        .astype(str)
        .str.fullmatch(
            r"\d+",
            na=False
        )
    )

    df = df[
        ~numeric_location_mask
    ].copy()

    # --------------------------------------------------------
    # Add District
    # --------------------------------------------------------

    df["District"] = district_name

    # --------------------------------------------------------
    # Remove obvious header artifacts
    # --------------------------------------------------------

    df = remove_header_artifacts(df)

    # --------------------------------------------------------
    # Return cleaned beneficiary data
    # --------------------------------------------------------

    final_columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village",
        "Name of the FRA beneficiary"
    ]

    df = df[
        final_columns
    ].reset_index(
        drop=True
    )

    return df


# ============================================================
# 9. CREATE VILLAGE SUMMARY
# ============================================================

def create_village_summary(clean_df):

    if clean_df.empty:

        return pd.DataFrame(
            columns=SUMMARY_COLUMNS
        )

    summary = (
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

    return summary


# ============================================================
# 10. CLEAN AN EXISTING DISTRICT SUMMARY
# ============================================================

def clean_existing_summary(
    summary,
    district
):

    if summary.empty:

        return summary

    # Make sure required columns exist

    for column in SUMMARY_COLUMNS:

        if column not in summary.columns:

            return None

    summary = summary[
        SUMMARY_COLUMNS
    ].copy()

    # Clean text

    for column in [
        "District",
        "Block",
        "Gram Panchayat",
        "Village"
    ]:

        summary[column] = (
            summary[column]
            .apply(clean_text)
        )

    # Remove obvious header artifacts

    before = len(summary)

    summary = remove_header_artifacts(
        summary
    )

    removed = before - len(summary)

    if removed > 0:

        print(
            f"{district}: removed "
            f"{removed} old header artifacts."
        )

    # Make sure district is correct

    summary["District"] = district

    # Remove exact duplicate village records

    summary = (
        summary
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

    # Make count numeric

    summary["Beneficiary_Count"] = pd.to_numeric(
        summary["Beneficiary_Count"],
        errors="coerce"
    )

    summary = summary[
        summary["Beneficiary_Count"]
        .notna()
    ].copy()

    summary["Beneficiary_Count"] = (
        summary["Beneficiary_Count"]
        .astype(int)
    )

    return summary


# ============================================================
# 11. PROCESS ONE DISTRICT
# ============================================================

def process_district(district):

    raw_district_path = os.path.join(
        RAW_DATA_PATH,
        district
    )

    cleaned_district_path = os.path.join(
        CLEANED_DATA_PATH,
        district
    )

    os.makedirs(
        cleaned_district_path,
        exist_ok=True
    )

    summary_path = os.path.join(
        cleaned_district_path,
        f"{district}_Village_Summary.csv"
    )

    # --------------------------------------------------------
    # EXISTING SUMMARY
    # --------------------------------------------------------

    if os.path.exists(summary_path):

        print(
            f"\n{district}: existing summary found."
        )

        try:

            summary = pd.read_csv(
                summary_path
            )

            summary = clean_existing_summary(
                summary,
                district
            )

            if summary is not None:

                summary.to_csv(
                    summary_path,
                    index=False
                )

                print(
                    f"{district}: loaded "
                    f"{len(summary)} villages."
                )

                return summary

        except Exception as error:

            print(
                f"{district}: existing summary "
                f"could not be used."
            )

            print(error)

            print(
                "Reprocessing PDFs..."
            )

    # --------------------------------------------------------
    # FIND PDFs
    # --------------------------------------------------------

    if not os.path.isdir(
        raw_district_path
    ):

        print(
            f"{district}: raw folder not found."
        )

        return None

    pdf_files = sorted(
        [
            file
            for file in os.listdir(
                raw_district_path
            )
            if file.lower().endswith(".pdf")
        ]
    )

    print(
        f"{district}: {len(pdf_files)} PDF(s) found."
    )

    if not pdf_files:

        print(
            f"{district}: no PDF found."
        )

        return None

    # --------------------------------------------------------
    # PROCESS ALL PDFS
    # --------------------------------------------------------

    cleaned_parts = []

    for number, pdf_file in enumerate(
        pdf_files,
        start=1
    ):

        print(
            f"\n{district}: PDF "
            f"{number}/{len(pdf_files)}"
        )

        pdf_path = os.path.join(
            raw_district_path,
            pdf_file
        )

        raw_df = extract_pdf_tables(
            pdf_path
        )

        if raw_df.empty:

            print(
                "No data extracted."
            )

            continue

        clean_df = clean_fra_data(
            raw_df,
            district
        )

        print(
            "Cleaned beneficiary rows:",
            len(clean_df)
        )

        if not clean_df.empty:

            cleaned_parts.append(
                clean_df
            )

    # --------------------------------------------------------
    # COMBINE ALL PDFs OF DISTRICT
    # --------------------------------------------------------

    if not cleaned_parts:

        print(
            f"{district}: no usable data."
        )

        return None

    combined_df = pd.concat(
        cleaned_parts,
        ignore_index=True
    )

    print(
        f"{district}: total cleaned beneficiary "
        f"rows = {len(combined_df)}"
    )

    # --------------------------------------------------------
    # CREATE VILLAGE SUMMARY
    # --------------------------------------------------------

    summary = create_village_summary(
        combined_df
    )

    # --------------------------------------------------------
    # SAVE DISTRICT SUMMARY
    # --------------------------------------------------------

    summary.to_csv(
        summary_path,
        index=False
    )

    print(
        f"{district}: village summary saved."
    )

    print(
        "Total villages:",
        len(summary)
    )

    return summary


# ============================================================
# 12. MAIN PIPELINE
# ============================================================

def main():

    print(
        "\n================================================"
    )

    print(
        "ODISHA FRA DATA CLEANING PIPELINE"
    )

    print(
        "================================================"
    )

    # --------------------------------------------------------
    # Find district folders
    # --------------------------------------------------------

    if not os.path.isdir(
        RAW_DATA_PATH
    ):

        print(
            f"ERROR: {RAW_DATA_PATH} not found."
        )

        return

    districts = sorted(
        [
            folder
            for folder in os.listdir(
                RAW_DATA_PATH
            )
            if os.path.isdir(
                os.path.join(
                    RAW_DATA_PATH,
                    folder
                )
            )
        ]
    )

    print(
        f"\nDistrict folders found: "
        f"{len(districts)}"
    )

    print(districts)

    all_summaries = []

    successful = []

    failed = []

    # --------------------------------------------------------
    # Process districts
    # --------------------------------------------------------

    for district in districts:

        print(
            "\n================================================"
        )

        print(
            f"PROCESSING: {district}"
        )

        print(
            "================================================"
        )

        try:

            summary = process_district(
                district
            )

            if summary is not None:

                all_summaries.append(
                    summary
                )

                successful.append(
                    district
                )

            else:

                failed.append(
                    district
                )

        except Exception as error:

            print(
                f"\nERROR in {district}:"
            )

            print(error)

            failed.append(
                district
            )

    # --------------------------------------------------------
    # CREATE MASTER DATASET
    # --------------------------------------------------------

    print(
        "\n================================================"
    )

    print(
        "CREATING MASTER DATASET"
    )

    print(
        "================================================"
    )

    if not all_summaries:

        print(
            "No usable district data found."
        )

        return

    master_df = pd.concat(
        all_summaries,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Final header-artifact removal
    # --------------------------------------------------------

    master_df = remove_header_artifacts(
        master_df
    )

    # --------------------------------------------------------
    # Remove exact duplicate village keys
    # --------------------------------------------------------

    master_df = (
        master_df
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
    # Remove invalid counts
    # --------------------------------------------------------

    master_df["Beneficiary_Count"] = pd.to_numeric(
        master_df["Beneficiary_Count"],
        errors="coerce"
    )

    master_df = master_df[
        master_df["Beneficiary_Count"]
        .notna()
    ].copy()

    master_df = master_df[
        master_df["Beneficiary_Count"] > 0
    ].copy()

    master_df["Beneficiary_Count"] = (
        master_df["Beneficiary_Count"]
        .astype(int)
    )

    # --------------------------------------------------------
    # Save master
    # --------------------------------------------------------

    master_path = os.path.join(
        CLEANED_DATA_PATH,
        "Odisha_FRA_Village_Master.csv"
    )

    master_df.to_csv(
        master_path,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print(
        "\n================================================"
    )

    print(
        "FINAL MASTER DATASET"
    )

    print(
        "================================================"
    )

    print(
        "District folders found:",
        len(districts)
    )

    print(
        "Successfully processed:",
        len(successful)
    )

    print(
        "Failed:",
        len(failed)
    )

    print(
        "Districts in master:",
        master_df["District"].nunique()
    )

    print(
        "Total village records:",
        len(master_df)
    )

    print(
        "Missing District:",
        master_df["District"].isna().sum()
    )

    print(
        "Missing Block:",
        master_df["Block"].isna().sum()
    )

    print(
        "Missing Gram Panchayat:",
        master_df[
            "Gram Panchayat"
        ].isna().sum()
    )

    print(
        "Missing Village:",
        master_df["Village"].isna().sum()
    )

    print(
        "Missing Beneficiary Count:",
        master_df[
            "Beneficiary_Count"
        ].isna().sum()
    )

    print(
        "Duplicate village keys:",
        master_df.duplicated(
            subset=[
                "District",
                "Block",
                "Gram Panchayat",
                "Village"
            ]
        ).sum()
    )

    print(
        "\nMaster file:"
    )

    print(
        master_path
    )

    print(
        "\n================================================"
    )

    print(
        "PIPELINE COMPLETED SUCCESSFULLY"
    )

    print(
        "================================================"
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()