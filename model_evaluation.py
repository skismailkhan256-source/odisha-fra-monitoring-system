
import os
import json
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)

# ==========================================
# FILE PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "Cleaned")

KMEANS_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_KMeans_Clustered.csv"
)

HIERARCHICAL_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Hierarchical_Clustered.csv"
)

OUTPUT_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Model_Evaluation.json"
)

# ==========================================
# LOAD EXISTING CLUSTERING RESULTS
# ==========================================

kmeans_df = pd.read_csv(KMEANS_FILE)
hierarchical_df = pd.read_csv(HIERARCHICAL_FILE)

features = [
    "Beneficiary_Count",
    "Village_Share_in_GP",
    "Village_Share_in_Block",
    "Village_Share_in_District"
]

required_kmeans = features + ["KMeans_Cluster"]
required_hierarchical = features + [
    "KMeans_Cluster",
    "Hierarchical_Cluster"
]

for column in required_kmeans:
    if column not in kmeans_df.columns:
        raise ValueError(f"Missing column in K-Means CSV: {column}")

for column in required_hierarchical:
    if column not in hierarchical_df.columns:
        raise ValueError(
            f"Missing column in Hierarchical CSV: {column}"
        )

# ==========================================
# SCALE FEATURES
# ==========================================

scaler = StandardScaler()

X_kmeans = scaler.fit_transform(
    kmeans_df[features]
)

X_hierarchical = scaler.transform(
    hierarchical_df[features]
)

# ==========================================
# EVALUATION FUNCTION
# ==========================================

def evaluate_clustering(X, labels, model_name):

    labels = pd.Series(labels).reset_index(drop=True)

    unique_clusters = labels.nunique()

    if unique_clusters < 2 or unique_clusters >= len(labels):
        raise ValueError(
            f"{model_name}: Invalid number of clusters for evaluation."
        )

    silhouette = silhouette_score(
        X,
        labels,
        sample_size=min(3000, len(labels)),
        random_state=42
    )

    davies_bouldin = davies_bouldin_score(
        X,
        labels
    )

    calinski_harabasz = calinski_harabasz_score(
        X,
        labels
    )

    return {
        "clusters": int(unique_clusters),
        "silhouette": round(float(silhouette), 4),
        "davies_bouldin": round(float(davies_bouldin), 4),
        "calinski_harabasz": round(float(calinski_harabasz), 2)
    }


# ==========================================
# K-MEANS EVALUATION
# ==========================================

kmeans_metrics = evaluate_clustering(
    X_kmeans,
    kmeans_df["KMeans_Cluster"],
    "K-Means"
)

# ==========================================
# HIERARCHICAL EVALUATION
# ==========================================

hierarchical_metrics = evaluate_clustering(
    X_hierarchical,
    hierarchical_df["Hierarchical_Cluster"],
    "Hierarchical"
)

# ==========================================
# PCA RESULTS
# ==========================================

from sklearn.decomposition import PCA

pca = PCA(n_components=2)
pca.fit(X_hierarchical)

pc1 = float(pca.explained_variance_ratio_[0] * 100)
pc2 = float(pca.explained_variance_ratio_[1] * 100)

pca_results = {
    "pc1": round(pc1, 2),
    "pc2": round(pc2, 2),
    "total_variance": round(pc1 + pc2, 2)
}

# ==========================================
# FINAL RESULTS
# ==========================================

results = {
    "total_villages": int(len(kmeans_df)),
    "kmeans": kmeans_metrics,
    "hierarchical": hierarchical_metrics,
    "pca": pca_results
}

# ==========================================
# SAVE JSON
# ==========================================

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(results, file, indent=4)

# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n===== K-MEANS EVALUATION =====")
print(kmeans_metrics)

print("\n===== HIERARCHICAL EVALUATION =====")
print(hierarchical_metrics)

print("\n===== PCA ANALYSIS =====")
print(pca_results)

print("\n===== FINAL MODEL COMPARISON =====")

comparison = pd.DataFrame([
    {
        "Model": "K-Means",
        **kmeans_metrics
    },
    {
        "Model": "Hierarchical",
        **hierarchical_metrics
    }
])

print(comparison.to_string(index=False))

print("\nEvaluation results saved successfully:")
print(OUTPUT_FILE)
