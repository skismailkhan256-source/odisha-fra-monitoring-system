
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Odisha FRA Monitoring System",
    page_icon="🌳",
    layout="wide"
)

VILLAGE_FILE = "data/Cleaned/Odisha_FRA_Featured_Master.csv"
STATUS_FILE = "data/Cleaned/Odisha_FRA_Monitoring_Analysis.csv"

# Dashboard styling
st.markdown("""
<style>
.stApp {
    background: #F4F8F3;
}
[data-testid="stSidebar"] {
    background: #E5EFE5;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #20392B !important;
}
.stApp h1, .stApp h2, .stApp h3,
.stApp p, .stApp label {
    color: #20392B;
}
.hero {
    background: linear-gradient(115deg, #164531, #347651);
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 22px;
}
.hero h1, .hero p, .hero span {
    color: #FFFFFF !important;
}
.hero h1 {
    font-size: 32px;
    margin-bottom: 8px;
}
.hero p {
    font-size: 16px;
}
.eyebrow {
    color: #D4E9D8 !important;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 700;
}
.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #20543B;
    margin-top: 18px;
    margin-bottom: 8px;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 18px;
    border: 1px solid #D9E5DA;
    border-radius: 12px;
    box-shadow: 0 2px 6px #163C2510;
}
[data-testid="stMetricLabel"] {
    color: #55715D !important;
}
[data-testid="stMetricValue"] {
    color: #20543B !important;
}
[data-testid="stCaptionContainer"] {
    color: #586F5C !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid #D9E5DA;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    villages = pd.read_csv(VILLAGE_FILE)
    monitoring = pd.read_csv(STATUS_FILE)
    return villages, monitoring


try:
    villages, monitoring = load_data()
except FileNotFoundError as error:
    st.error(f"Dataset file not found: {error}")
    st.stop()


# Standardize district names for matching
def district_key(name):
    name = str(name).strip().upper()

    aliases = {
        "ANGUL": "ANUGUL",
        "BALASORE": "BALESHWAR",
        "BHADRAKH": "BHADRAK",
        "BOLANGIR": "BALANGIR",
        "BOUDH": "BAUDH",
        "CUTTACKK": "CUTTACK",
        "DEOGARH": "DEBAGARH",
        "JAGATSINGHPUR": "JAGATSINGHAPUR",
        "JAGATSINGPUR": "JAGATSINGHAPUR",
        "JAJPUR": "JAJAPUR",
        "JHARUGUDA": "JHARSUGUDA",
        "KENDRAPADA": "KENDRAPARA",
        "KEONJHAR": "KENDUJHAR",
        "KHURDA": "KHORDHA"
    }

    return aliases.get(name, name)


villages["District_Key"] = villages["District"].apply(district_key)
monitoring["District_Key"] = monitoring["District"].apply(district_key)


def fmt(value):
    if pd.isna(value):
        return "N/A"
    return f"{int(value):,}"


# Sidebar filters
with st.sidebar:
    st.markdown("## 🌳 FRA Monitor")
    st.caption("Odisha • Forest Rights Act, 2006")
    st.divider()

    district_names = sorted(
        monitoring["District"].dropna().unique().tolist(),
        key=str.casefold
    )

    default_index = next(
        (
            i for i, name in enumerate(district_names)
            if str(name).strip().upper() == "MAYURBHANJ"
        ),
        0
    )

    selected_district = st.selectbox(
        "Search or select district",
        district_names,
        index=default_index
    )

    st.divider()
    st.markdown("**Project information**")
    st.caption("Implementation data: 30 September 2025")
    st.caption(f"Districts in source: {len(district_names)}")
    st.caption("Village data is available for some districts only.")


selected_key = district_key(selected_district)

district_rows = monitoring[
    monitoring["District_Key"] == selected_key
]

village_data = villages[
    villages["District_Key"] == selected_key
].copy()

if district_rows.empty:
    st.error("District record not found.")
    st.stop()

district = district_rows.iloc[0]


# Header
st.markdown("""
<div class="hero">
    <div class="eyebrow">FOREST RIGHTS ACT • ODISHA</div>
    <h1>Odisha FRA Monitoring System</h1>
    <p>District implementation status, village analysis and review priorities</p>
    <span>District monitoring dashboard • Data as of 30 September 2025</span>
</div>
""", unsafe_allow_html=True)


# Section 1: district overview
st.markdown(
    f'<div class="section-title">{selected_district} — Overview</div>',
    unsafe_allow_html=True
)

st.caption("Official source figures are available at district level.")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Claims Filed", fmt(district["Claims_Filed"]))
c2.metric("Claims Approved", fmt(district["Claims_Approved"]))
c3.metric("Claims Rejected", fmt(district["Claims_Rejected"]))
c4.metric("Titles Distributed", fmt(district["Titles_Distributed"]))

c1, c2, c3, c4 = st.columns(4)

c1.metric("Approval Rate", f'{district["Approval_Rate"]:.2f}%')
c2.metric("Rejection Rate", f'{district["Rejection_Rate"]:.2f}%')
c3.metric(
    "Title Distribution Rate",
    f'{district["Title_Distribution_Rate"]:.2f}%'
)
c4.metric("Forest Land (Ha)", fmt(district["Forest_Land_Titles_Ha"]))


# Section 2: implementation progress
st.markdown(
    '<div class="section-title">Implementation Progress</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Remaining Claims (Derived)",
    fmt(district["Remaining_Claims"])
)
c2.metric(
    "Implementation Gap (Derived)",
    fmt(district["Implementation_Gap"])
)
c3.metric(
    "District Review Category",
    str(district["Monitoring_Priority"])
)

st.caption(
    "Remaining Claims = Filed − Approved − Rejected. This is a derived "
    "estimate, not an official pending-claims figure. Implementation Gap "
    "= Approved − Titles Distributed."
)


# Section 3: charts
st.markdown(
    '<div class="section-title">District Analytics</div>',
    unsafe_allow_html=True
)

chart1, chart2 = st.columns(2)

with chart1:
    st.markdown("#### Claim Status")

    claim_data = pd.DataFrame({
        "Status": [
            "Filed", "Approved", "Rejected", "Titles Distributed"
        ],
        "Count": [
            district["Claims_Filed"],
            district["Claims_Approved"],
            district["Claims_Rejected"],
            district["Titles_Distributed"]
        ]
    })

    fig = px.bar(
        claim_data,
        x="Status",
        y="Count",
        color="Status",
        text="Count",
        color_discrete_map={
            "Filed": "#245A40",
            "Approved": "#3A865B",
            "Rejected": "#C45650",
            "Titles Distributed": "#B79B3B"
        }
    )

    fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside"
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#20392B",
        yaxis_title="Number of claims",
        xaxis_title="",
        margin=dict(t=30, b=20, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)


with chart2:
    st.markdown("#### Village Review Categories")

    if village_data.empty:
        st.info(
            "Village-level beneficiary data is not available "
            "for this district."
        )
    else:
        priority_counts = (
            village_data["Village_Monitoring_Priority"]
            .value_counts()
            .reindex(["High", "Medium", "Low"], fill_value=0)
            .rename_axis("Priority")
            .reset_index(name="Village Records")
        )

        fig = px.bar(
            priority_counts,
            x="Priority",
            y="Village Records",
            color="Priority",
            text="Village Records",
            color_discrete_map={
                "High": "#C45650",
                "Medium": "#D3A43D",
                "Low": "#3A865B"
            }
        )
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#20392B",
            xaxis_title="",
            yaxis_title="Village records",
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)


# Section 4: top villages
st.markdown(
    '<div class="section-title">Villages to Review First</div>',
    unsafe_allow_html=True
)

st.caption(
    "Top 10 villages by beneficiary count. This is a review list, "
    "not a ranking by pending FRA claims."
)

if village_data.empty:
    st.warning(
        "Village-level beneficiary data is unavailable for this district."
    )
else:
    village_data["Beneficiary_Count"] = pd.to_numeric(
        village_data["Beneficiary_Count"],
        errors="coerce"
    ).fillna(0)

    top_villages = village_data.sort_values(
        "Beneficiary_Count",
        ascending=False
    ).head(10)

    top_table = top_villages[
        [
            "Block",
            "Gram Panchayat",
            "Village",
            "Beneficiary_Count",
            "Village_Monitoring_Priority"
        ]
    ].rename(columns={
        "Block": "Block",
        "Gram Panchayat": "Gram Panchayat",
        "Village": "Village Name",
        "Beneficiary_Count": "Beneficiaries",
        "Village_Monitoring_Priority": "Review Category"
    })

    st.dataframe(
        top_table,
        use_container_width=True,
        hide_index=True,
        height=390
    )


# Section 5: village explorer
st.markdown(
    '<div class="section-title">Village Explorer</div>',
    unsafe_allow_html=True
)

if village_data.empty:
    st.warning(
        "Village records cannot be shown because village-level "
        "beneficiary data is not available for this district."
    )
else:
    f1, f2, f3 = st.columns(3)

    block_options = ["All Blocks"] + sorted(
        village_data["Block"].dropna().unique().tolist()
    )

    with f1:
        selected_block = st.selectbox(
            "Filter by Block",
            block_options,
            key=f"block_{selected_key}"
        )

    filtered = village_data.copy()

    if selected_block != "All Blocks":
        filtered = filtered[
            filtered["Block"] == selected_block
        ]

    gp_options = ["All Gram Panchayats"] + sorted(
        filtered["Gram Panchayat"].dropna().unique().tolist()
    )

    with f2:
        selected_gp = st.selectbox(
            "Filter by Gram Panchayat",
            gp_options,
            key=f"gp_{selected_key}_{selected_block}"
        )

    with f3:
        selected_priority = st.selectbox(
            "Filter by Review Category",
            ["All", "High", "Medium", "Low"],
            key=f"priority_{selected_key}"
        )

    search_text = st.text_input(
        "Search village name",
        placeholder="Type the village name here..."
    )

    if selected_gp != "All Gram Panchayats":
        filtered = filtered[
            filtered["Gram Panchayat"] == selected_gp
        ]

    if selected_priority != "All":
        filtered = filtered[
            filtered["Village_Monitoring_Priority"] == selected_priority
        ]

    if search_text.strip():
        filtered = filtered[
            filtered["Village"].astype(str).str.contains(
                search_text.strip(),
                case=False,
                na=False
            )
        ]

    filtered = filtered.sort_values(
        "Beneficiary_Count",
        ascending=False
    )

    st.write(f"**Matching village records: {len(filtered):,}**")

    table = filtered[
        [
            "Block",
            "Gram Panchayat",
            "Village",
            "Beneficiary_Count",
            "Village_Monitoring_Priority"
        ]
    ].rename(columns={
        "Village": "Village Name",
        "Beneficiary_Count": "Beneficiaries",
        "Village_Monitoring_Priority": "Review Category"
    })

    if filtered.empty:
        st.info(
            "No matching villages. Try All Blocks, All Gram Panchayats "
            "and All review categories."
        )
    else:
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            height=420
        )

        st.download_button(
            "Download filtered village report",
            data=table.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{selected_district}_village_report.csv",
            mime="text/csv"
        )


# Section 6: methodology
with st.expander("Data sources, methodology and limitations"):
    st.markdown("**District implementation data**")
    st.write(
        "Claims filed, approved, rejected, titles distributed and forest "
        "land are based on the implementation dataset dated 30 September 2025."
    )

    st.markdown("**Village data**")
    st.write(
        "The village master includes District, Block, Gram Panchayat, Village "
        "and Beneficiary Count. It does not provide verified village-level "
        "approved, rejected or pending claims."
    )

    st.markdown("**Village review categories**")
    st.write(
        "High: more than 50 beneficiaries. Medium: 11–50. "
        "Low: 10 or fewer. These are analytical categories, not official "
        "government FRA priorities."
    )

    missing = monitoring.loc[
        monitoring["Beneficiary_Data_Available"] == "No",
        "District"
    ].tolist()

    if missing:
        st.markdown("**Districts without village beneficiary data**")
        st.write(", ".join(missing))

    st.markdown("**Derived metrics**")
    st.write(
        "Remaining Claims = Claims Filed − Claims Approved − Claims Rejected."
    )
    st.write(
        "Implementation Gap = Claims Approved − Titles Distributed."
    )
