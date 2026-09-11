# Odisha FRA Monitoring System - Data Dictionary

## Dataset Name

Odisha FRA Village Master Dataset

**File:** `Odisha_FRA_Village_Master.csv`

## Purpose

This dataset contains cleaned and merged village-level Forest Rights Act (FRA) beneficiary information from the available district-wise FRA beneficiary records of Odisha.

It is prepared for further analysis, feature engineering, monitoring-priority analysis, and dashboard development.

## Dataset Coverage

- Districts covered: 25
- Village records: 12,464
- Missing values: 0
- Duplicate village records: 0

## Columns

| Column | Data Type | Description | Example |
|---|---|---|---|
| District | Text | Name of the district associated with the village. | Angul |
| Block | Text | Name of the administrative block. | ANGUL |
| Gram Panchayat | Text | Name of the Gram Panchayat associated with the village. | JAGANNATHPUR |
| Village | Text | Name of the village or area. | TARAVA |
| Beneficiary_Count | Integer | Number of FRA beneficiary records associated with the village in the processed source data. | 23 |

## Column Description

### District
Identifies the district where the village is located.

### Block
Identifies the administrative block associated with the village.

### Gram Panchayat
Identifies the Gram Panchayat associated with the village.

### Village
Identifies the village or area associated with the FRA records.

### Beneficiary_Count
Represents the number of FRA beneficiary records associated with each village in the processed source data.

A higher value means more beneficiary records are associated with that village in the available source data.

## Data Processing

The dataset was created using an automated Python data-processing pipeline.

### Processing Flow

District FRA PDFs
↓
PDF Table Extraction
↓
Text Cleaning
↓
OCR / Duplicate-Text Cleaning
↓
'-do-' Continuation Handling
↓
Location Recovery
↓
Header Artifact Removal
↓
District-wise Village Summary
↓
25 Districts Merged
↓
Odisha_FRA_Village_Master.csv
↓
Quality Validation

## Quality Validation

The final dataset was checked for:

- Missing values
- Duplicate village records
- Invalid beneficiary counts
- PDF header artifacts
- Suspicious village names

### Final Validation Result

- Districts: 25
- Village Records: 12,464
- Missing Values: 0
- Duplicate Records: 0
- Header Artifacts: 0
- Zero/Negative Beneficiary Counts: 0

## Important Note

`Beneficiary_Count` represents the number of beneficiary records available in the processed FRA source data.

It does not by itself represent:

- Approved claims
- Pending claims
- Rejected claims
- Titles distributed
- Legal eligibility
- Monitoring priority

Additional FRA indicators may be integrated later for feature engineering and monitoring-priority analysis.

## Intended Use

This master dataset is the base dataset for the Odisha FRA Monitoring System.

It can be used for:

1. Village-level FRA analysis
2. Feature engineering
3. Monitoring-priority analysis
4. Data visualization
5. Web dashboard development
6. Integration with additional FRA datasets

## Responsible Use

The dataset is intended for analytical and monitoring decision support.

Any priority score or classification developed later should be treated as an analytical indicator and not as a legal decision regarding FRA claims.