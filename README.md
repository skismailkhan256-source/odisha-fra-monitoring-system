# Odisha FRA Monitoring System
### AI & WebGIS Based Forest Rights Act Monitoring Platform

An academic MCA project that brings available Forest Rights Act (FRA) implementation records and village-level beneficiary information into one platform for data analysis, monitoring and geographical exploration.

---

## 1. Project Overview

The **Odisha FRA Monitoring System** is a data analytics and WebGIS-based web application developed to organise, analyse and explore available FRA-related information for Odisha.

FRA implementation information is available in different district reports, PDF documents and village-level beneficiary records. Examining these records separately makes comparison and monitoring difficult.

This project processes the available records, prepares structured datasets, performs feature engineering and machine-learning analysis, and presents the results through an interactive web application.

The system is designed for data exploration and academic decision-support demonstration. It does not replace official government records or make legal decisions regarding FRA claims.

## 2. Project Aim

The main aim is to develop an integrated monitoring platform that makes available FRA implementation information easier to access, analyse and understand.

The platform combines district-level implementation statistics with village-level beneficiary records and provides analytical indicators, clustering results, geographical visualisation and downloadable reports.

## 3. Project Objectives

- Extract village-level beneficiary information from district-wise FRA PDF documents.
- Clean, validate and standardise the collected records.
- Prepare district, block, Gram Panchayat and village-level analytical features.
- Calculate beneficiary totals and relative village-share indicators.
- Apply K-Means and Hierarchical Clustering to explore village-level patterns.
- Evaluate clustering results using standard evaluation metrics.
- Use PCA for dimensionality reduction and visual analysis.
- Develop a web application with dashboard, analytics, ML and WebGIS modules.
- Provide CSV downloads for further analysis.

## 4. Project Workflow

The project follows an end-to-end data-processing and application-development workflow:

1. **Data Collection:** Collect district-wise FRA beneficiary PDFs and the district implementation-status report.
2. **Data Extraction:** Extract tabular information from PDF documents using PDFPlumber.
3. **Data Cleaning:** Handle invalid records, repeated headers, formatting issues and administrative-name variations.
4. **Dataset Preparation:** Prepare the village master dataset and separate district implementation-status dataset.
5. **Feature Engineering:** Calculate Gram Panchayat, block and district totals, village counts and beneficiary-share features.
6. **Feature Scaling:** Apply StandardScaler to the numerical features before clustering.
7. **Machine Learning:** Apply K-Means and Hierarchical Clustering to identify similar village-level numerical patterns.
8. **Model Evaluation:** Evaluate clustering results using Silhouette Score, Davies-Bouldin Index and Calinski-Harabasz Score.
9. **PCA Analysis:** Reduce the scaled feature space into two principal components for visual exploration.
10. **Web Integration:** Integrate prepared datasets and analytical outputs into the Flask application.
11. **Visualisation and Reporting:** Display dashboard indicators, charts, maps and downloadable CSV reports.

## 5. Dataset Description

The project uses two principal data sources.

### A. Village-Level Beneficiary Dataset

Village-wise FRA beneficiary information extracted from available district PDF records.

| Information | Details |
|---|---|
| Initial village master | 12,464 records |
| Final featured dataset | 12,424 records |
| District coverage | 25 districts |
| Total beneficiary records | 271,328 |
| Final dataset columns | 16 |
| Missing cells in final dataset | 0 |
| Exact duplicate rows | 0 |

### B. District-Level Implementation Dataset

A separate dataset prepared from the FRA implementation-status statement.

It contains 30 district records and includes indicators such as:

- Claims filed
- Claims approved
- Claims rejected
- Titles distributed
- FRA committees
- Forest-land title area

**Important:** The district implementation dataset and village beneficiary dataset have different source coverage. They are maintained separately and should not be treated as one fully reconciled official database.

## 6. Feature Engineering

Feature engineering is used to understand village beneficiary counts in relation to their administrative areas.

The project creates features such as:

- GP_Total_Beneficiaries
- Block_Total_Beneficiaries
- District_Total_Beneficiaries
- GP_Village_Count
- Block_Village_Count
- District_Village_Count
- Village_Share_in_GP
- Village_Share_in_Block
- Village_Share_in_District
- Beneficiary_Category
- Village_Monitoring_Priority

Beneficiary categories are defined using project-based rules:

| Category | Beneficiary Count |
|---|---:|
| Low | 10 or fewer |
| Medium | 11–50 |
| High | More than 50 |

These are analytical categories defined by the project. They are not official government priority classifications.

## 7. Machine Learning Methodology

The project uses unsupervised learning to explore similarities among village-level beneficiary records.

### K-Means Clustering

- Number of clusters: 5
- Random state: 42
- Initialisations (`n_init`): 10
- Feature scaling: StandardScaler

### Hierarchical Clustering

- Method: Agglomerative hierarchical clustering
- Linkage: Ward
- Number of clusters: 6
- Feature scaling: StandardScaler

### Numerical Features Used

1. Beneficiary_Count
2. Village_Share_in_GP
3. Village_Share_in_Block
4. Village_Share_in_District

### Model Evaluation Results

| Evaluation Metric | K-Means (5 Clusters) | Hierarchical (6 Clusters) |
|---|---:|---:|
| Silhouette Score | 0.5942 | 0.5449 |
| Davies-Bouldin Index | 0.6249 | 0.6121 |
| Calinski-Harabasz Score | 6756.02 | 6089.03 |

The evaluation results show that K-Means performs better on the Silhouette and Calinski-Harabasz metrics, while Hierarchical Clustering has a lower Davies-Bouldin Index. Therefore, neither method is considered universally superior across all evaluation metrics.

### PCA Analysis

Principal Component Analysis is applied to the scaled clustering features.

- PC1 explained variance: 39.38%
- PC2 explained variance: 22.44%
- Combined explained variance: 61.82%

PCA helps represent the four-dimensional feature space in two dimensions. Explained variance is not a clustering accuracy score.

## 8. Application Modules

The web application contains the following modules:

| Module | Description |
|---|---|
| Home | Introduces the project and provides navigation. |
| Dashboard | Displays summary indicators, claims overview and charts. |
| District Analytics | Shows district-specific implementation statistics. |
| Village Explorer | Provides village search and District, Block and Gram Panchayat filters. |
| ML Priority Analysis | Displays clustering results, cluster summaries and evaluation metrics. |
| WebGIS | Provides district-level beneficiary choropleth visualisation and an interactive geographical map. |
| Reports & Data Export | Provides downloadable district, village and clustering CSV files. |
| About | Explains the project, technology stack, objectives and limitations. |

## 9. Technology Stack

| Area | Technologies |
|---|---|
| Programming Language | Python 3.11 |
| Data Processing | Pandas, NumPy |
| PDF Extraction | PDFPlumber |
| Data Visualisation | Plotly |
| Machine Learning | Scikit-learn |
| Clustering and Scientific Computing | SciPy |
| Dimensionality Reduction | PCA |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Geographical Visualisation | GeoJSON, Leaflet, OpenStreetMap |
| Deployment Support | Gunicorn |

## 10. Project Architecture

The system is organised into the following logical layers:

**Source Data → Extraction → Data Cleaning → Feature Engineering → Machine Learning → Flask Backend → Frontend & WebGIS → Reports and Visualisation**

- Source layer: FRA PDF documents, processed CSV files and geographical boundaries.
- Processing layer: PDF extraction, cleaning, validation and aggregation.
- Analytics layer: Feature engineering, clustering and PCA.
- Backend layer: Flask routes, data loading, APIs and CSV downloads.
- Presentation layer: HTML, CSS, JavaScript, charts and interactive maps.

## 11. Project Limitations

- The platform uses the available source records and their existing coverage.
- Village-level and district-level datasets have different coverage.
- Village-level geographical coordinates have not been verified.
- Clustering labels are analytical groupings, not official FRA priorities.
- The system does not independently verify individual legal claims or eligibility.
- It does not provide official village-level pending-claim status or automated administrative decisions.
- The project is an academic prototype, not a production government monitoring system.

## 12. Future Scope

- Integrate updated and authorised FRA records from official sources.
- Improve district and village dataset reconciliation.
- Validate village and Gram Panchayat geographical coordinates.
- Add stronger automated tests for data quality and application functionality.
- Improve cluster interpretation with documented profiles and domain review.
- Add time-based comparisons when comparable historical datasets become available.
- Introduce role-based access and audit logs for future operational use.

## 13. Installation and Setup

### Prerequisites

- Python 3.11
- Git
- pip

### Step 1: Clone the Repository

```bash
git clone https://github.com/skismailkhan256-source/odisha-fra-monitoring-system.git
```

### Step 2: Open the Project Directory

```bash
cd odisha-fra-monitoring-system
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

Open the local address displayed in your terminal in a web browser.

**Note:** These are the standard setup steps for the Flask application. Check the repository's current requirements and configuration if your local setup requires additional environment variables or commands.

## 14. Repository

GitHub Repository:

https://github.com/skismailkhan256-source/odisha-fra-monitoring-system

## 15. Live Demo

The deployed version of the Odisha FRA Monitoring System can be accessed here:

Live Application: https://odisha-fra-monitoring-system.onrender.com

## 16. Project Team

| Team Member | Registration Number |
|---|---|
| SK Ismail | 2503320100153 |
| Deepak Rajak | 2503320100216 |
| Amit Kumar Shaw | 2503320100215 |
| Raktim Karan | 2503320100207 |

**Project Guide:** Mr. Girish Dhal

**Department:** Department of Computer Applications  
**University:** Centurion University of Technology and Management  
**Campus:** Bhubaneswar  
**Academic Session:** 2026–2027

---

## 17. Disclaimer

This project is developed for academic purposes. All analytical indicators, beneficiary categories and machine-learning cluster labels are intended for data exploration and decision-support demonstration only. They do not represent official government classifications, legal eligibility decisions or verified administrative priorities.
