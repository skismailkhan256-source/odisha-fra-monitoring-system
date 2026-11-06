import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Load dataset
df = pd.read_csv("data/Cleaned/Odisha_FRA_Featured_Master.csv")

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

# Generate cluster labels
df["KMeans_Cluster"] = kmeans.fit_predict(X)

# Save clustered dataset
output_path = "data/Cleaned/Odisha_FRA_KMeans_Clustered.csv"
df.to_csv(output_path, index=False)

# Display results
print("===== K-Means Clustering Completed =====")
print("Number of Clusters:", df["KMeans_Cluster"].nunique())

print("\nCluster Sizes:")
print(df["KMeans_Cluster"].value_counts().sort_index())

print("\nSaved successfully:", output_path)