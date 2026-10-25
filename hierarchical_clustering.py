import pandas as pd
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import linkage, fcluster

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

# Hierarchical clustering using Ward linkage
Z = linkage(X, method="ward")

# Create 6 clusters
df["Hierarchical_Cluster"] = fcluster(
    Z,
    t=6,
    criterion="maxclust"
)

# Save output
output_path = "data/Cleaned/Odisha_FRA_Hierarchical_Clustered.csv"
df.to_csv(output_path, index=False)

print("===== Hierarchical Clustering Completed =====")
print("Number of Clusters:", df["Hierarchical_Cluster"].nunique())
print("\nCluster Sizes:")
print(df["Hierarchical_Cluster"].value_counts().sort_index())
print("\nSaved successfully:", output_path)

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# PCA for 2D visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# Plot Hierarchical clusters
plt.figure(figsize=(10, 7))

scatter = plt.scatter(
    X_pca[:, 0],
    X_pca[:, 1],
    c=df["Hierarchical_Cluster"],
    s=15,
    alpha=0.7
)

plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("Hierarchical Clustering - PCA Visualization")
plt.colorbar(scatter, label="Cluster")

plt.tight_layout()
plt.show()

print("\nPCA Explained Variance:")
print("PC1:", round(pca.explained_variance_ratio_[0], 4))
print("PC2:", round(pca.explained_variance_ratio_[1], 4))
print(
    "Total:",
    round(pca.explained_variance_ratio_.sum(), 4)
)