import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Odisha FRA Monitoring System",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATA PATH
# ============================================================

DATA_PATH = "data/Cleaned/Odisha_FRA_Final_ML_Dataset.csv"


# ============================================================
# CSS ONLY
# ============================================================

st.markdown(
    """
    <style>

    /* Remove Streamlit top header */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Remove toolbar */
    [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Remove footer */
    footer {
        display: none !important;
    }

    /* Main application */
    .stApp {
        background-color: #031f18;
    }

    .main {
        background-color: #031f18;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #062c23 !important;
        border-right: 1px solid #1d5b4e;
    }

    /* Normal text */
    .stMarkdown,
    p,
    label {
        color: #dce8e5;
    }

    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: #202129 !important;
        border: 1px solid #315c54 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Text input */
    input {
        background-color: #202129 !important;
        color: #ffffff !important;
        border-color: #315c54 !important;
    }

    /* Metric */
    [data-testid="stMetric"] {
        background-color: #0b3a31;
        border: 1px solid #287865;
        border-radius: 14px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #9fc0b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #245c50;
        border-radius: 8px;
    }

    /* Info / warning / success boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Horizontal line */
    hr {
        border-color: #1d5147 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_csv(DATA_PATH)

    # Clean column names
    data.columns = data.columns.str.strip()

    # Clean text columns
    text_columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village",
        "priority_level",
        "ml_priority_level"
    ]

    for column in text_columns:

        if column in data.columns:

            data[column] = (
                data[column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
            )

    # Clean numeric columns
    numeric_columns = [
        "Beneficiary_Count",
        "priority_score",
        "beneficiary_score",
        "beneficiary_density_score",
        "conflict_score"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

    return data


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_data()

except FileNotFoundError:

    st.error(
        "Dataset not found.\n\n"
        "Expected location:\n"
        "`data/Cleaned/Odisha_FRA_Final_ML_Dataset.csv`"
    )

    st.stop()

except Exception as error:

    st.error(
        f"Error loading dataset: {error}"
    )

    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def number(value):

    try:
        return f"{int(round(value)):,}"

    except Exception:
        return "0"


def filter_district(data, district):

    if district == "All Districts":
        return data.copy()

    return data[
        data["District"] == district
    ].copy()


def priority_counts(data):

    if "ml_priority_level" not in data.columns:

        return 0, 0, 0

    values = (
        data["ml_priority_level"]
        .astype(str)
        .str.title()
        .value_counts()
    )

    high = int(values.get("High", 0))
    medium = int(values.get("Medium", 0))
    low = int(values.get("Low", 0))

    return high, medium, low


def village_count(data):

    if "Village" in data.columns:
        return data["Village"].nunique()

    return len(data)


def beneficiary_count(data):

    if "Beneficiary_Count" not in data.columns:
        return 0

    return data["Beneficiary_Count"].sum()


def block_count(data):

    if "Block" not in data.columns:
        return 0

    return data["Block"].nunique()


def panchayat_count(data):

    if "Gram Panchayat" not in data.columns:
        return 0

    return data["Gram Panchayat"].nunique()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🌳 Odisha FRA")

    st.caption("Monitoring System")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🎯 Priority Analysis",
            "🗺️ WebGIS Map",
            "🔎 Village Explorer"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### Project")

    st.caption(
        "Forest Rights Act Monitoring"
    )

    st.markdown("### Technology")

    st.caption(
        "Streamlit • ML • WebGIS"
    )

    st.markdown("### Role")

    st.caption(
        "Member 4 — Streamlit & Final Application"
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.title(
        "🌳 Odisha FRA Monitoring System"
    )

    st.caption(
        "Forest Rights Act • Village-level monitoring "
        "and decision support for Odisha"
    )

    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    districts = sorted(
        df["District"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_district = st.selectbox(
        "Select District",
        ["All Districts"] + districts,
        key="dashboard_district"
    )

    data = filter_district(
        df,
        selected_district
    )

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    st.subheader("Overview")

    villages = village_count(data)

    beneficiaries = beneficiary_count(data)

    blocks = block_count(data)

    panchayats = panchayat_count(data)

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🏘️ Total Villages",
            number(villages),
            help="Village records monitored"
        )

    with c2:

        st.metric(
            "👥 Beneficiaries",
            number(beneficiaries),
            help="Recorded beneficiaries"
        )

    with c3:

        st.metric(
            "🏢 Blocks",
            number(blocks),
            help="Administrative blocks"
        )

    with c4:

        st.metric(
            "🏛️ Gram Panchayats",
            number(panchayats),
            help="Gram Panchayats covered"
        )

    st.divider()

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    chart1, chart2 = st.columns(
        [1.35, 1]
    )

    # --------------------------------------------------------
    # BENEFICIARIES BY BLOCK
    # --------------------------------------------------------

    with chart1:

        st.subheader(
            "📊 Beneficiaries by Block"
        )

        if (
            "Block" in data.columns
            and "Beneficiary_Count" in data.columns
        ):

            block_data = (
                data
                .groupby("Block", as_index=False)
                ["Beneficiary_Count"]
                .sum()
                .sort_values(
                    "Beneficiary_Count",
                    ascending=True
                )
                .tail(12)
            )

            fig = px.bar(
                block_data,
                x="Beneficiary_Count",
                y="Block",
                orientation="h",
                text="Beneficiary_Count"
            )

            fig.update_traces(
                marker_color="#45b98b",
                textposition="outside"
            )

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#dce8e5",
                margin=dict(
                    l=10,
                    r=30,
                    t=20,
                    b=20
                ),
                xaxis=dict(
                    title="Beneficiaries",
                    gridcolor="#19473e"
                ),
                yaxis=dict(
                    title="",
                    gridcolor="rgba(0,0,0,0)"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )

    # --------------------------------------------------------
    # PRIORITY DISTRIBUTION
    # --------------------------------------------------------

    with chart2:

        st.subheader(
            "🎯 ML Priority Distribution"
        )

        high, medium, low = priority_counts(
            data
        )

        priority_data = pd.DataFrame(
            {
                "Priority": [
                    "Low",
                    "Medium",
                    "High"
                ],
                "Count": [
                    low,
                    medium,
                    high
                ]
            }
        )

        fig = px.pie(
            priority_data,
            names="Priority",
            values="Count",
            hole=0.58
        )

        fig.update_traces(
            textinfo="label+percent"
        )

        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dce8e5",
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    # --------------------------------------------------------
    # PRIORITY SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "🎯 ML Priority Summary"
    )

    high, medium, low = priority_counts(
        data
    )

    if "priority_score" in data.columns:

        average_score = data[
            "priority_score"
        ].mean()

    else:

        average_score = 0

    s1, s2, s3, s4 = st.columns(4)

    with s1:

        st.metric(
            "🔴 High Priority",
            number(high)
        )

    with s2:

        st.metric(
            "🟠 Medium Priority",
            number(medium)
        )

    with s3:

        st.metric(
            "🟢 Low Priority",
            number(low)
        )

    with s4:

        st.metric(
            "📊 Average Score",
            f"{average_score:.2f}"
        )

    # --------------------------------------------------------
    # HIGHEST PRIORITY VILLAGES
    # --------------------------------------------------------

    st.subheader(
        "🔴 Highest Priority Villages"
    )

    columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village",
        "Beneficiary_Count",
        "priority_score",
        "ml_priority_level"
    ]

    available_columns = [
        col
        for col in columns
        if col in data.columns
    ]

    if "priority_score" in data.columns:

        highest = (
            data
            .sort_values(
                "priority_score",
                ascending=False
            )
            [available_columns]
            .head(10)
            .copy()
        )

        highest = highest.rename(
            columns={
                "Beneficiary_Count":
                    "Beneficiaries",

                "priority_score":
                    "Priority Score",

                "ml_priority_level":
                    "ML Priority"
            }
        )

        st.dataframe(
            highest,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.caption(
        "🌳 Odisha FRA Monitoring System"
    )

    st.caption(
        "Forest Rights Act • Data Monitoring • "
        "ML Priority • WebGIS"
    )


# ============================================================
# PRIORITY ANALYSIS
# ============================================================

elif page == "🎯 Priority Analysis":

    st.title(
        "🎯 ML Priority Analysis"
    )

    st.caption(
        "Village-level monitoring using the ML priority "
        "dataset prepared by Member 2"
    )

    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    districts = sorted(
        df["District"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_district = st.selectbox(
        "Select District",
        ["All Districts"] + districts,
        key="priority_district"
    )

    data = filter_district(
        df,
        selected_district
    )

    high, medium, low = priority_counts(
        data
    )

    if "priority_score" in data.columns:

        average_score = data[
            "priority_score"
        ].mean()

    else:

        average_score = 0

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "🔴 High Priority",
            number(high)
        )

    with c2:
        st.metric(
            "🟠 Medium Priority",
            number(medium)
        )

    with c3:
        st.metric(
            "🟢 Low Priority",
            number(low)
        )

    with c4:
        st.metric(
            "📊 Average Score",
            f"{average_score:.2f}"
        )

    # --------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "Priority Distribution"
    )

    priority_data = pd.DataFrame(
        {
            "Priority Level": [
                "High",
                "Medium",
                "Low"
            ],
            "Villages": [
                high,
                medium,
                low
            ]
        }
    )

    fig = px.bar(
        priority_data,
        x="Priority Level",
        y="Villages",
        text="Villages"
    )

    fig.update_traces(
        marker_color="#45b98b",
        textposition="outside"
    )

    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce8e5",
        xaxis=dict(
            gridcolor="rgba(0,0,0,0)"
        ),
        yaxis=dict(
            gridcolor="#19473e"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

    # --------------------------------------------------------
    # SCORE DISTRIBUTION
    # --------------------------------------------------------

    st.subheader(
        "Priority Score Distribution"
    )

    if "priority_score" in data.columns:

        fig = px.histogram(
            data,
            x="priority_score",
            nbins=20
        )

        fig.update_traces(
            marker_color="#73b6e6"
        )

        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#dce8e5",
            xaxis=dict(
                title="Priority Score",
                gridcolor="#19473e"
            ),
            yaxis=dict(
                title="Number of Villages",
                gridcolor="#19473e"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    # --------------------------------------------------------
    # TOP VILLAGES
    # --------------------------------------------------------

    st.subheader(
        "🔴 Highest Priority Villages"
    )

    columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village",
        "Beneficiary_Count",
        "priority_score",
        "ml_priority_level"
    ]

    available_columns = [
        col
        for col in columns
        if col in data.columns
    ]

    top_data = (
        data
        .sort_values(
            "priority_score",
            ascending=False
        )
        [available_columns]
        .head(15)
        .copy()
    )

    top_data = top_data.rename(
        columns={
            "Beneficiary_Count":
                "Beneficiaries",

            "priority_score":
                "Priority Score",

            "ml_priority_level":
                "ML Priority"
        }
    )

    st.dataframe(
        top_data,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    st.info(
        "The priority score and ML priority level are derived "
        "from the feature-engineered ML dataset. They are used "
        "for monitoring and decision-support purposes."
    )

    st.divider()

    st.caption(
        "🌳 Odisha FRA Monitoring System • "
        "ML Priority Analysis"
    )


# ============================================================
# WEBGIS MAP
# ============================================================

elif page == "🗺️ WebGIS Map":

    st.title(
        "🗺️ WebGIS Map"
    )

    st.caption(
        "Village-level geographic visualization for FRA monitoring"
    )

    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    st.info(
        "The WebGIS layer is prepared for integration with "
        "validated village-level geographic data. Once latitude, "
        "longitude or boundary information is available, the "
        "geographic layer can be displayed here."
    )

    st.subheader(
        "Available Geographic Records"
    )

    # --------------------------------------------------------
    # CHECK COORDINATES
    # --------------------------------------------------------

    latitude_columns = [
        "latitude",
        "Latitude",
        "lat"
    ]

    longitude_columns = [
        "longitude",
        "Longitude",
        "lon"
    ]

    latitude_found = None
    longitude_found = None

    for column in latitude_columns:

        if column in df.columns:

            latitude_found = column
            break

    for column in longitude_columns:

        if column in df.columns:

            longitude_found = column
            break

    if (
        latitude_found is not None
        and longitude_found is not None
    ):

        st.success(
            "Geographic coordinates detected."
        )

        map_data = df[
            [
                latitude_found,
                longitude_found
            ]
        ].dropna()

        if len(map_data) > 0:

            map_data = map_data.rename(
                columns={
                    latitude_found: "lat",
                    longitude_found: "lon"
                }
            )

            st.map(
                map_data
            )

    else:

        st.warning(
            "📍 Geographic coordinate data is not available "
            "in the current ML dataset."
        )

    st.metric(
        "Village Records",
        number(
            village_count(df)
        )
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.subheader(
        "Geographic Data Preview"
    )

    preview_columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village"
    ]

    preview_columns = [
        col
        for col in preview_columns
        if col in df.columns
    ]

    st.dataframe(
        df[preview_columns].head(10),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.caption(
        "🌳 Odisha FRA Monitoring System • WebGIS"
    )


# ============================================================
# VILLAGE EXPLORER
# ============================================================

elif page == "🔎 Village Explorer":

    st.title(
        "🔎 Village Explorer"
    )

    st.caption(
        "Search and inspect village-level FRA information"
    )

    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    districts = sorted(
        df["District"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_district = st.selectbox(
        "Select District",
        ["All Districts"] + districts,
        key="explorer_district"
    )

    data = filter_district(
        df,
        selected_district
    )

    # --------------------------------------------------------
    # BLOCK
    # --------------------------------------------------------

    blocks = sorted(
        data["Block"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_block = st.selectbox(
        "Select Block",
        ["All Blocks"] + blocks,
        key="explorer_block"
    )

    if selected_block != "All Blocks":

        data = data[
            data["Block"] == selected_block
        ].copy()

    # --------------------------------------------------------
    # VILLAGE SEARCH
    # --------------------------------------------------------

    search = st.text_input(
        "Search Village",
        placeholder="Type a village name..."
    )

    if search:

        data = data[
            data["Village"]
            .str.contains(
                search.strip(),
                case=False,
                na=False
            )
        ].copy()

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    st.subheader(
        f"{number(len(data))} records found"
    )

    columns = [
        "District",
        "Block",
        "Gram Panchayat",
        "Village",
        "Beneficiary_Count",
        "priority_score",
        "ml_priority_level"
    ]

    available_columns = [
        col
        for col in columns
        if col in data.columns
    ]

    result = data[
        available_columns
    ].head(100).copy()

    result = result.rename(
        columns={
            "Beneficiary_Count":
                "Beneficiaries",

            "priority_score":
                "Priority Score",

            "ml_priority_level":
                "ML Priority"
        }
    )

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Showing the first 100 matching records. "
        "Use the filters above to narrow the results."
    )

    st.divider()

    st.caption(
        "🌳 Odisha FRA Monitoring System • Village Explorer"
    )