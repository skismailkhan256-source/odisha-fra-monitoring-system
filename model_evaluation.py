import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

# Load dataset
df = pd.read_csv("data/Cleaned/Odisha_FRA_KMeans_Clustered.csv")

# Features used for clustering
features = [
    "Beneficiary_Count",
    "Village_Share_in_GP",
    "Village_Share_in_Block",
    "Village_Share_in_District"
]

# Scale features
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# K-Means model
kmeans = KMeans(
    n_clusters=5,
    random_state=42,
    n_init=10
)

labels = kmeans.fit_predict(X)

# Evaluation metrics
silhouette = silhouette_score(
    X, labels,
    sample_size=3000,
    random_state=42
)

davies_bouldin = davies_bouldin_score(X, labels)

calinski_harabasz = calinski_harabasz_score(X, labels)

# Display results
print("---- K-Means Model Evaluation ---- ")
print("Number of Clusters:", 5)
print("Silhouette Score:", round(silhouette, 4))
print("Davies-Bouldin Index:", round(davies_bouldin, 4))
print("Calinski-Harabasz Score:", round(calinski_harabasz, 2))

from scipy.cluster.hierarchy import linkage, fcluster

# Hierarchical Clustering
Z = linkage(X, method="ward")

# Create 6 clusters
hierarchical_labels = fcluster(
    Z,
    t=6,
    criterion="maxclust"
)

# Evaluation metrics
hierarchical_silhouette = silhouette_score(
    X,
    hierarchical_labels,
    sample_size=3000,
    random_state=42
)

hierarchical_davies_bouldin = davies_bouldin_score(
    X,
    hierarchical_labels
)

hierarchical_calinski_harabasz = calinski_harabasz_score(
    X,
    hierarchical_labels
)

# Display results
print("\n===== Hierarchical Clustering Evaluation =====")
print("Number of Clusters:", 6)
print("Silhouette Score:", round(hierarchical_silhouette, 4))
print("Davies-Bouldin Index:", round(hierarchical_davies_bouldin, 4))
print(
    "Calinski-Harabasz Score:",
    round(hierarchical_calinski_harabasz, 2)
)

# Final Model Comparison

comparison = pd.DataFrame({
    "Model": ["K-Means", "Hierarchical"],
    "Silhouette Score": [silhouette, hierarchical_silhouette],
    "Davies-Bouldin Index": [davies_bouldin, hierarchical_davies_bouldin],
    "Calinski-Harabasz Score": [
        calinski_harabasz,
        hierarchical_calinski_harabasz
    ]
})

print("\n===== Final Model Comparison =====")
print(comparison.to_string(index=False))