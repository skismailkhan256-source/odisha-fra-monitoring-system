import pandas as pd

input_file = "data/Cleaned/Odisha_FRA_District_Merged_Analysis.csv"
output_file = "data/Cleaned/Odisha_FRA_Monitoring_Analysis.csv"

df = pd.read_csv(input_file)

print("Loading merged dataset...")
print("Rows:", len(df))


# Approval rate
df["Approval_Rate"] = (
    df["Claims_Approved"] / df["Claims_Filed"] * 100
).round(2)


# Rejection rate
df["Rejection_Rate"] = (
    df["Claims_Rejected"] / df["Claims_Filed"] * 100
).round(2)


# Title distribution rate
df["Title_Distribution_Rate"] = (
    df["Titles_Distributed"] / df["Claims_Approved"] * 100
).round(2)


# Remaining claims after approved and rejected
df["Remaining_Claims"] = (
    df["Claims_Filed"]
    - df["Claims_Approved"]
    - df["Claims_Rejected"]
)


# Implementation gap
df["Implementation_Gap"] = (
    df["Claims_Approved"] - df["Titles_Distributed"]
)


# Monitoring priority
def get_priority(row):
    if row["Remaining_Claims"] > 10000 or row["Implementation_Gap"] > 2000:
        return "High"
    elif row["Remaining_Claims"] > 5000 or row["Implementation_Gap"] > 1000:
        return "Medium"
    else:
        return "Low"


df["Monitoring_Priority"] = df.apply(
    get_priority,
    axis=1
)


df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


print("\nMonitoring metrics created.")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nPriority:")
print(df["Monitoring_Priority"].value_counts())

print("\nSaved at:")
print(output_file)