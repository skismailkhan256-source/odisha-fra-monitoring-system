# ==================================================
# ODISHA FRA MONITORING SYSTEM
# COMPLETE UPDATED FLASK APPLICATION
# ==================================================

from flask import (
    Flask,
    render_template,
    request,
    make_response,
    jsonify,
    send_file,
    Response
)

import pandas as pd
import os
import json


app = Flask(__name__)


# ==================================================
# HEALTH CHECK - FOR DEPLOYMENT MONITORING
# ==================================================

@app.route("/health", methods=["GET"])
def health():
    """Lightweight endpoint for deployment health checks."""

    return jsonify({
        "status": "healthy",
        "application": "Odisha FRA Monitoring System"
    }), 200


# ==================================================
# 1. DATASET PATHS
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "Cleaned")

VILLAGE_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Featured_Master.csv"
)

MONITORING_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Monitoring_Analysis.csv"
)

KMEANS_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_KMeans_Clustered.csv"
)

HIERARCHICAL_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Hierarchical_Clustered.csv"
)

MODEL_EVALUATION_FILE = os.path.join(
    DATA_DIR,
    "Odisha_FRA_Model_Evaluation.json"
)

GEOJSON_MAP_FILE = os.path.join(
    BASE_DIR,
    "data",
    "geo",
    "odisha_fra_choropleth.html"
)


# ==================================================
# 2. DATA LOADING
# ==================================================

def load_data():

    villages = pd.read_csv(VILLAGE_FILE)
    monitoring = pd.read_csv(MONITORING_FILE)
    kmeans = pd.read_csv(KMEANS_FILE)
    hierarchical = pd.read_csv(HIERARCHICAL_FILE)

    return villages, monitoring, kmeans, hierarchical


def load_villages():

    return pd.read_csv(VILLAGE_FILE).reset_index(drop=True)


# ==================================================
# 3. HELPER FUNCTIONS
# ==================================================

def safe_int(value):

    if pd.isna(value):
        return 0

    return int(value)


def safe_float(value):

    if pd.isna(value):
        return 0.0

    return float(value)


def get_cluster_distribution(data, column):

    if column not in data.columns:
        raise ValueError(
            f"Required clustering column '{column}' not found."
        )

    counts = (
        data[column]
        .dropna()
        .value_counts()
        .sort_index()
    )

    labels = [
        f"Cluster {int(cluster)}"
        for cluster in counts.index
    ]

    values = [
        int(count)
        for count in counts.values
    ]

    return labels, values


def filter_villages(data, district="", block="", gp=""):

    filtered = data.copy()

    if district:
        filtered = filtered[
            filtered["District"].astype(str) == district
        ]

    if block:
        filtered = filtered[
            filtered["Block"].astype(str) == block
        ]

    if gp:
        filtered = filtered[
            filtered["Gram Panchayat"].astype(str) == gp
        ]

    return filtered


def village_label(row):

    return (
        f"{row['Village']} | "
        f"{row['Gram Panchayat']} | "
        f"{row['Block']} | "
        f"{row['District']}"
    )


# ==================================================
# 4. LANDING HOMEPAGE
# ==================================================

@app.route("/")
def home():

    return render_template("home.html")


# ==================================================
# 5. MAIN DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    try:

        villages, monitoring, kmeans, hierarchical = load_data()

        total_districts = int(
            monitoring["District"].nunique()
        )

        total_claims = safe_int(
            monitoring["Claims_Filed"].sum()
        )

        total_approved = safe_int(
            monitoring["Claims_Approved"].sum()
        )

        total_rejected = safe_int(
            monitoring["Claims_Rejected"].sum()
        )

        total_titles = safe_int(
            monitoring["Titles_Distributed"].sum()
        )

        total_villages = int(len(villages))

        total_beneficiaries = safe_int(
            villages["Beneficiary_Count"].sum()
        )

        priority_counts = {
            str(key): int(value)
            for key, value in
            monitoring["Monitoring_Priority"]
            .value_counts()
            .items()
        }

        top_districts = (
            monitoring
            .sort_values(
                by="Claims_Filed",
                ascending=False
            )
            .head(10)
            .to_dict(orient="records")
        )

        top_villages = (
            villages
            .sort_values(
                by="Beneficiary_Count",
                ascending=False
            )
            .head(10)
            .to_dict(orient="records")
        )

        return render_template(
            "dashboard.html",
            total_districts=total_districts,
            total_claims=total_claims,
            total_approved=total_approved,
            total_rejected=total_rejected,
            total_titles=total_titles,
            total_villages=total_villages,
            total_beneficiaries=total_beneficiaries,
            priority_counts=priority_counts,
            top_districts=top_districts,
            top_villages=top_villages
        )

    except FileNotFoundError as error:

        app.logger.exception("Dashboard dataset not found")
        return f"Dataset file not found: {error}", 500

    except Exception as error:

        app.logger.exception("Dashboard loading failed")
        return f"Dashboard error: {error}", 500


# ==================================================
# 6. DISTRICT ANALYTICS
# ==================================================

@app.route("/district")
def district():

    try:

        _, monitoring, _, _ = load_data()

        districts = sorted(
            monitoring["District"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_district = request.args.get(
            "district",
            districts[0] if districts else ""
        )

        if selected_district not in districts:
            selected_district = (
                districts[0] if districts else ""
            )

        district_data = monitoring[
            monitoring["District"] == selected_district
        ]

        if district_data.empty:
            return "District record not found", 404

        district_record = district_data.iloc[0].to_dict()

        return render_template(
            "district.html",
            districts=districts,
            selected_district=selected_district,
            district=district_record
        )

    except Exception as error:

        app.logger.exception(
            "District analytics loading failed"
        )

        return f"District page error: {error}", 500


# ==================================================
# 7. ML PRIORITY ANALYSIS
# ==================================================

@app.route("/ml-analysis")
def ml_analysis():

    try:

        kmeans = pd.read_csv(KMEANS_FILE)
        hierarchical = pd.read_csv(HIERARCHICAL_FILE)

        if not os.path.exists(MODEL_EVALUATION_FILE):
            return (
                "Model evaluation JSON file not found. "
                "Please run model_evaluation.py first.",
                500
            )

        with open(
            MODEL_EVALUATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            evaluation = json.load(file)

        kmeans_labels, kmeans_values = get_cluster_distribution(
            kmeans,
            "KMeans_Cluster"
        )

        total_kmeans_clusters = len(kmeans_labels)

        hierarchical_labels, hierarchical_values = (
            get_cluster_distribution(
                hierarchical,
                "Hierarchical_Cluster"
            )
        )

        total_hierarchical_clusters = len(
            hierarchical_labels
        )

        total_villages = int(len(kmeans))

        required_columns = [
            "Beneficiary_Count",
            "KMeans_Cluster"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in kmeans.columns
        ]

        if missing_columns:
            raise ValueError(
                f"K-Means dataset is missing columns: {missing_columns}"
            )

        cluster_summary = []

        for cluster_id, group in kmeans.groupby(
            "KMeans_Cluster",
            dropna=True
        ):

            village_count = int(len(group))

            total_beneficiaries = safe_int(
                pd.to_numeric(
                    group["Beneficiary_Count"],
                    errors="coerce"
                ).fillna(0).sum()
            )

            average_beneficiaries = round(
                total_beneficiaries / village_count,
                2
            ) if village_count else 0

            if "District" in group.columns:

                district_counts = (
                    group["District"]
                    .dropna()
                    .astype(str)
                    .value_counts()
                )

                top_district = (
                    str(district_counts.index[0])
                    if not district_counts.empty
                    else "Not Available"
                )

            else:

                top_district = "Not Available"

            priority_counts = {
                "High": 0,
                "Medium": 0,
                "Low": 0
            }

            if "Village_Monitoring_Priority" in group.columns:

                actual_counts = (
                    group["Village_Monitoring_Priority"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .str.title()
                    .value_counts()
                )

                for priority in priority_counts:

                    priority_counts[priority] = int(
                        actual_counts.get(priority, 0)
                    )

            cluster_summary.append({

                "cluster": int(cluster_id),
                "village_count": village_count,
                "total_beneficiaries": total_beneficiaries,
                "average_beneficiaries": average_beneficiaries,
                "top_district": top_district,
                "high": priority_counts["High"],
                "medium": priority_counts["Medium"],
                "low": priority_counts["Low"]

            })

        cluster_summary.sort(
            key=lambda item: item["cluster"]
        )

        model_metrics = {
            "kmeans": evaluation["kmeans"],
            "hierarchical": evaluation["hierarchical"]
        }

        pca_results = {
            "pc1": evaluation["pca"]["pc1"],
            "pc2": evaluation["pca"]["pc2"],
            "total_variance": evaluation["pca"]["total_variance"]
        }

        return render_template(
            "ml_analysis.html",
            total_villages=total_villages,
            total_kmeans_clusters=total_kmeans_clusters,
            total_hierarchical_clusters=total_hierarchical_clusters,
            kmeans_labels=kmeans_labels,
            kmeans_values=kmeans_values,
            hierarchical_labels=hierarchical_labels,
            hierarchical_values=hierarchical_values,
            model_metrics=model_metrics,
            pca_results=pca_results,
            cluster_summary=cluster_summary
        )

    except FileNotFoundError as error:

        app.logger.exception(
            "ML Analysis dataset file not found"
        )

        return f"ML dataset file not found: {error}", 500

    except KeyError as error:

        app.logger.exception(
            "Required evaluation key is missing"
        )

        return (
            f"Evaluation JSON is missing required key: {error}",
            500
        )

    except Exception as error:

        app.logger.exception(
            "ML Analysis page loading failed"
        )

        return f"ML Analysis error: {error}", 500


# ==================================================
# 8. VILLAGE SEARCH API
# ==================================================

@app.route("/api/villages")
def village_search_api():

    try:

        villages = load_villages()

        query = request.args.get("q", "").strip()
        district = request.args.get("district", "").strip()
        block = request.args.get("block", "").strip()
        gp = request.args.get("gp", "").strip()

        filtered = filter_villages(
            villages,
            district=district,
            block=block,
            gp=gp
        )

        if query:
            filtered = filtered[
                filtered["Village"]
                .astype(str)
                .str.contains(
                    query,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        results = []

        for index, row in filtered.head(50).iterrows():

            results.append({
                "id": int(index),
                "village": str(row["Village"]),
                "gp": str(row["Gram Panchayat"]),
                "block": str(row["Block"]),
                "district": str(row["District"]),
                "label": village_label(row)
            })

        return jsonify(results)

    except Exception as error:

        app.logger.exception("Village search API failed")

        return jsonify({
            "error": str(error)
        }), 500


# ==================================================
# 9. DISTRICT-DEPENDENT BLOCK API
# ==================================================

@app.route("/api/blocks")
def blocks_api():

    try:

        villages = load_villages()

        district = request.args.get(
            "district", ""
        ).strip()

        if not district:
            return jsonify([])

        filtered = villages[
            villages["District"].astype(str) == district
        ]

        blocks = sorted(
            filtered["Block"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        return jsonify(blocks)

    except Exception as error:

        app.logger.exception("Block API failed")

        return jsonify({
            "error": str(error)
        }), 500


# ==================================================
# 10. BLOCK-DEPENDENT GRAM PANCHAYAT API
# ==================================================

@app.route("/api/gram-panchayats")
def gram_panchayats_api():

    try:

        villages = load_villages()

        district = request.args.get(
            "district", ""
        ).strip()

        block = request.args.get(
            "block", ""
        ).strip()

        if not district or not block:
            return jsonify([])

        filtered = villages[
            (villages["District"].astype(str) == district) &
            (villages["Block"].astype(str) == block)
        ]

        gps = sorted(
            filtered["Gram Panchayat"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        return jsonify(gps)

    except Exception as error:

        app.logger.exception("Gram Panchayat API failed")

        return jsonify({
            "error": str(error)
        }), 500


# ==================================================
# 11. DISTRICT-WISE FRA SUMMARY API
# ==================================================

@app.route("/api/district-summary")
def district_summary_api():

    try:

        villages = load_villages()

        district = request.args.get(
            "district", ""
        ).strip()

        if not district:
            return jsonify({
                "error": "District name is required"
            }), 400

        required_columns = [
            "District",
            "Block",
            "Gram Panchayat",
            "Village",
            "Beneficiary_Count"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in villages.columns
        ]

        if missing_columns:
            return jsonify({
                "error": "Required columns are missing",
                "missing_columns": missing_columns
            }), 500

        district_values = (
            villages["District"]
            .astype(str)
            .str.strip()
            .str.casefold()
        )

        filtered = villages.loc[
            district_values == district.casefold()
        ].copy()

        if filtered.empty:
            return jsonify({
                "error": f"No FRA records found for district: {district}"
            }), 404

        beneficiary_values = pd.to_numeric(
            filtered["Beneficiary_Count"],
            errors="coerce"
        ).fillna(0)

        village_keys = [
            "District",
            "Block",
            "Gram Panchayat",
            "Village"
        ]

        total_villages = int(
            filtered[village_keys]
            .dropna(subset=["Village"])
            .drop_duplicates()
            .shape[0]
        )

        total_blocks = int(
            filtered["Block"]
            .dropna()
            .astype(str)
            .str.strip()
            .nunique()
        )

        return jsonify({
            "district": str(filtered["District"].iloc[0]),
            "total_beneficiaries": int(beneficiary_values.sum()),
            "total_villages": total_villages,
            "total_blocks": total_blocks
        })

    except Exception as error:

        app.logger.exception("District summary API failed")

        return jsonify({
            "error": str(error)
        }), 500


# ==================================================
# 12. VILLAGE EXPLORER
# ==================================================

@app.route("/village")
def village():

    try:

        villages = load_villages()

        total_villages = int(len(villages))

        total_beneficiaries = safe_int(
            villages["Beneficiary_Count"].sum()
        )

        selected_district = request.args.get(
            "district", ""
        ).strip()

        selected_block = request.args.get(
            "block", ""
        ).strip()

        selected_gp = request.args.get(
            "gp", ""
        ).strip()

        selected_village = request.args.get(
            "village_id", ""
        ).strip()

        filtered = filter_villages(
            villages,
            district=selected_district,
            block=selected_block,
            gp=selected_gp
        )

        village_record = None

        if selected_village:

            try:

                village_id = int(selected_village)

                if 0 <= village_id < len(villages):

                    candidate = villages.iloc[village_id]

                    if village_id in filtered.index:
                        village_record = candidate.to_dict()

            except (ValueError, IndexError):

                village_record = None

        if request.args.get("download") == "csv":

            if village_record is None:
                return "Please select a valid village first.", 400

            csv_data = pd.DataFrame(
                [village_record]
            ).to_csv(
                index=False,
                encoding="utf-8-sig"
            )

            response = make_response(csv_data)

            response.headers["Content-Disposition"] = (
                "attachment; filename=Selected_Village_Details.csv"
            )

            response.headers["Content-Type"] = (
                "text/csv; charset=utf-8"
            )

            return response

        matching_villages = []

        if not selected_village and (
            selected_district or selected_block or selected_gp
        ):

            for index, row in filtered.head(100).iterrows():

                matching_villages.append({
                    "id": int(index),
                    "label": village_label(row),
                    "village": str(row["Village"]),
                    "district": str(row["District"]),
                    "block": str(row["Block"]),
                    "gp": str(row["Gram Panchayat"]),
                    "beneficiaries": safe_int(
                        row["Beneficiary_Count"]
                    )
                })

        districts = sorted(
            villages["District"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        blocks = []

        if selected_district:

            blocks = sorted(
                villages[
                    villages["District"].astype(str)
                    == selected_district
                ]["Block"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        gps = []

        if selected_district and selected_block:

            gps = sorted(
                villages[
                    (villages["District"].astype(str) == selected_district) &
                    (villages["Block"].astype(str) == selected_block)
                ]["Gram Panchayat"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

        return render_template(
            "village.html",
            total_villages=total_villages,
            total_beneficiaries=total_beneficiaries,
            districts=districts,
            blocks=blocks,
            gps=gps,
            selected_district=selected_district,
            selected_block=selected_block,
            selected_gp=selected_gp,
            selected_village=selected_village,
            village_record=village_record,
            matching_villages=matching_villages
        )

    except FileNotFoundError as error:

        app.logger.exception("Village dataset not found")
        return f"Village dataset not found: {error}", 500

    except Exception as error:

        app.logger.exception(
            "Village Explorer loading failed"
        )

        return f"Village Explorer error: {error}", 500


# ==================================================
# 13. WEBGIS MAP
# ==================================================

@app.route("/webgis")
def webgis():

    return render_template("webgis.html")


# ==================================================
# 14. WEBGIS BENEFICIARY CHOROPLETH MAP
# ==================================================

@app.route("/webgis/beneficiary-map")
def beneficiary_map():

    try:

        if not os.path.exists(GEOJSON_MAP_FILE):

            app.logger.error(
                "Beneficiary choropleth HTML file not found: %s",
                GEOJSON_MAP_FILE
            )

            return "Beneficiary map file not found.", 404

        # Read the existing Plotly map HTML without modifying the source file.
        with open(GEOJSON_MAP_FILE, "r", encoding="utf-8") as map_file:
            map_html = map_file.read()

        # Connect the district dropdown and Plotly map.
        interaction_script = r"""
<script>
(function () {
    "use strict";

    let graph = null;
    let selectedOverlayIndex = null;
    let baseTraceIndex = -1;
    let clickHandlerAttached = false;

    function normalizeDistrict(value) {
        return String(value || "")
            .trim()
            .toLocaleLowerCase()
            .replace(/\s+/g, " ");
    }

    function getDistrictSelect() {
        try {
            return window.parent.document.getElementById("districtSelect");
        } catch (error) {
            console.warn("Unable to access parent district selector:", error);
            return null;
        }
    }

    function findMapGraph() {
        return document.querySelector(".js-plotly-plot");
    }

    function findBaseChoropleth() {
        if (!graph || !graph.data) return -1;

        return graph.data.findIndex(function (trace) {
            return trace &&
                (trace.type === "choropleth" ||
                 trace.type === "choroplethmapbox") &&
                trace.geojson &&
                Array.isArray(trace.locations);
        });
    }

    async function highlightDistrict(districtName) {

        if (!graph || !window.Plotly || !districtName) return;

        const normalized = normalizeDistrict(districtName);

        // Remove the previous selected boundary.
        if (
            selectedOverlayIndex !== null &&
            selectedOverlayIndex < graph.data.length
        ) {
            await Plotly.deleteTraces(graph, selectedOverlayIndex);
            selectedOverlayIndex = null;
        }

        baseTraceIndex = findBaseChoropleth();

        if (baseTraceIndex < 0) {
            console.warn("No compatible Plotly choropleth trace was found.");
            return;
        }

        const baseTrace = graph.data[baseTraceIndex];

        const locations = baseTrace.locations || [];

        const features = (
            baseTrace.geojson &&
            Array.isArray(baseTrace.geojson.features)
        ) ? baseTrace.geojson.features : [];

        // Match the district name from GeoJSON properties.
        const matchedFeature = features.find(function (feature) {

            const properties = feature.properties || {};

            const featureDistrict =
                properties.FRA_District ||
                properties.District ||
                properties.shapeName ||
                "";

            return normalizeDistrict(featureDistrict) === normalized;
        });

        if (!matchedFeature) {
            console.warn("District not found in map GeoJSON:", districtName);
            return;
        }

        const featureId = matchedFeature.id;

        const matchedLocation = locations.find(function (location) {
            return String(location) === String(featureId);
        });

        if (matchedLocation === undefined) {
            console.warn(
                "District feature ID is not in Plotly locations:",
                featureId
            );
            return;
        }

        // Create a transparent overlay with a yellow boundary.
        const overlay = {
            type: baseTrace.type,
            geojson: baseTrace.geojson,
            featureidkey: baseTrace.featureidkey || "id",
            locations: [matchedLocation],
            z: [1],
            zmin: 0,
            zmax: 1,

            colorscale: [
                [0, "rgba(255, 193, 7, 0)"],
                [1, "rgba(255, 193, 7, 0)"]
            ],

            showscale: false,
            showlegend: false,
            hoverinfo: "skip",

            marker: {
                opacity: 1,
                line: {
                    color: "#ffc107",
                    width: 5
                }
            },

            name: "Selected district boundary"
        };

        await Plotly.addTraces(graph, overlay);

        selectedOverlayIndex = graph.data.length - 1;
    }

    function syncFromDropdown() {

        const districtSelect = getDistrictSelect();

        if (!districtSelect || !districtSelect.value) return;

        highlightDistrict(districtSelect.value);
    }

    function syncDropdownFromMap(districtName) {

        const districtSelect = getDistrictSelect();

        if (!districtSelect || !districtName) return;

        const target = normalizeDistrict(districtName);

        const matchingOption = Array.from(
            districtSelect.options
        ).find(function (option) {

            return normalizeDistrict(option.value) === target ||
                normalizeDistrict(option.textContent) === target;
        });

        if (!matchingOption) {
            console.warn(
                "Clicked district is not present in dropdown:",
                districtName
            );
            return;
        }

        districtSelect.value = matchingOption.value;

        // Trigger existing district statistics API.
        districtSelect.dispatchEvent(
            new Event("change", { bubbles: true })
        );
    }

    function attachMapEvents() {

        graph = findMapGraph();

        if (
            !graph ||
            !window.Plotly ||
            !graph.data ||
            !graph.on
        ) {
            return false;
        }

        baseTraceIndex = findBaseChoropleth();

        if (baseTraceIndex < 0) {
            console.warn(
                "The embedded Plotly chart is not a GeoJSON choropleth."
            );
            return true;
        }

        // Dropdown -> Map synchronization.
        const districtSelect = getDistrictSelect();

        if (
            districtSelect &&
            !districtSelect.dataset.mapSyncAttached
        ) {
            districtSelect.addEventListener(
                "change",
                syncFromDropdown
            );

            districtSelect.dataset.mapSyncAttached = "true";
        }

        // Map -> Dropdown synchronization.
        if (!clickHandlerAttached) {

            graph.on("plotly_click", function (eventData) {

                if (
                    !eventData ||
                    !eventData.points ||
                    !eventData.points.length
                ) {
                    return;
                }

                const point = eventData.points[0];

                if (point.curveNumber !== baseTraceIndex) return;

                const clickedLocation = point.location;

                const features =
                    graph.data[baseTraceIndex].geojson.features || [];

                const feature = features.find(function (item) {
                    return String(item.id) === String(clickedLocation);
                });

                if (!feature) return;

                const properties = feature.properties || {};

                const clickedDistrict =
                    properties.FRA_District ||
                    properties.District ||
                    properties.shapeName;

                if (!clickedDistrict) return;

                syncDropdownFromMap(clickedDistrict);
            });

            clickHandlerAttached = true;
        }

        // Highlight the initially selected district.
        syncFromDropdown();

        return true;
    }

    function initializeMapSync() {

        let attempts = 0;

        const timer = window.setInterval(function () {

            attempts += 1;

            if (attachMapEvents() || attempts >= 40) {
                window.clearInterval(timer);
            }

        }, 250);
    }

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initializeMapSync
        );

    } else {

        initializeMapSync();

    }

})();
</script>
"""

        # Inject interaction script into the map HTML.
        if "</body>" in map_html.lower():

            body_close_index = map_html.lower().rfind("</body>")

            map_html = (
                map_html[:body_close_index]
                + interaction_script
                + map_html[body_close_index:]
            )

        else:

            map_html += interaction_script

        return Response(
            map_html,
            mimetype="text/html"
        )

    except Exception as error:

        app.logger.exception(
            "Beneficiary map loading failed"
        )

        return f"Beneficiary map error: {error}", 500


# ==================================================
# 15. REPORTS PAGE
# ==================================================

@app.route("/reports")
def reports():

    try:

        villages = pd.read_csv(VILLAGE_FILE)
        monitoring = pd.read_csv(MONITORING_FILE)

        total_villages = int(len(villages))

        total_districts = int(
            monitoring["District"].nunique()
        )

        return render_template(
            "reports.html",
            total_villages=total_villages,
            total_districts=total_districts
        )

    except Exception as error:

        app.logger.exception("Reports page loading failed")

        return f"Reports error: {error}", 500


# ==================================================
# 16. DOWNLOAD REPORTS
# ==================================================

@app.route("/reports/download/<report_type>")
def download_report(report_type):

    report_files = {

        "district": (
            MONITORING_FILE,
            "Odisha_FRA_District_Monitoring_Report.csv"
        ),

        "village": (
            VILLAGE_FILE,
            "Odisha_FRA_Village_Master_Report.csv"
        ),

        "kmeans": (
            KMEANS_FILE,
            "Odisha_FRA_KMeans_Clustering_Report.csv"
        ),

        "hierarchical": (
            HIERARCHICAL_FILE,
            "Odisha_FRA_Hierarchical_Clustering_Report.csv"
        )

    }

    if report_type not in report_files:
        return "Invalid report type.", 404

    file_path, download_name = report_files[report_type]

    try:

        if not os.path.exists(file_path):
            return "Requested report dataset was not found.", 404

        response = make_response(
            pd.read_csv(file_path).to_csv(
                index=False,
                encoding="utf-8-sig"
            )
        )

        response.headers["Content-Disposition"] = (
            f'attachment; filename="{download_name}"'
        )

        response.headers["Content-Type"] = (
            "text/csv; charset=utf-8"
        )

        return response

    except Exception as error:

        app.logger.exception("Report download failed")

        return f"Report download error: {error}", 500


# ==================================================
# 17. ABOUT PROJECT
# ==================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ==================================================
# 18. RUN FLASK APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )