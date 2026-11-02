
// ==========================================
// ODISHA FRA MONITORING SYSTEM
// WEBGIS MAP FUNCTIONALITY
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // ======================================
    // 1. CHECK WEBGIS PAGE
    // ======================================

    const mapElement = document.getElementById("fraMap");

    // Stop execution on other pages
    if (!mapElement) {
        return;
    }

    // Check Leaflet library
    if (typeof L === "undefined") {

        console.error("Leaflet library is not loaded.");

        mapElement.innerHTML = `
            <div class="alert alert-danger m-3">
                Unable to load the map. Please check your internet connection.
            </div>
        `;

        return;
    }


    // ======================================
    // 2. ODISHA MAP CONFIGURATION
    // ======================================

    // Odisha geographical centre
    const odishaCenter = [20.15, 84.40];

    // Initial zoom level
    const initialZoom = 7;

    // Odisha approximate geographical bounds
    const odishaBounds = L.latLngBounds(
        [17.78, 81.35],
        [22.57, 87.55]
    );


    // ======================================
    // 3. INITIALIZE LEAFLET MAP
    // ======================================

    const fraMap = L.map("fraMap", {

        center: odishaCenter,

        zoom: initialZoom,

        zoomControl: true,

        scrollWheelZoom: true,

        doubleClickZoom: true,

        dragging: true,

        preferCanvas: true,

        minZoom: 5,

        maxZoom: 18

    });


    // Set initial Odisha view
    fraMap.setView(
        odishaCenter,
        initialZoom
    );


    // ======================================
    // 4. OPEN STREET MAP BASE LAYER
    // ======================================

    const osmLayer = L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',

            maxZoom: 19,

            minZoom: 5,

            updateWhenIdle: true,

            keepBuffer: 2

        }

    );


    // Add OpenStreetMap
    osmLayer.addTo(fraMap);


    // Handle tile loading errors
    osmLayer.on("tileerror", function (error) {

        console.warn(
            "OpenStreetMap tile loading issue:",
            error
        );

    });


    // ======================================
    // 5. MAP LAYER CONTROL
    // ======================================

    const baseMaps = {

        "OpenStreetMap": osmLayer

    };


    L.control.layers(

        baseMaps,

        null,

        {

            collapsed: true,

            position: "topright"

        }

    ).addTo(fraMap);


    // ======================================
    // 6. SCALE CONTROL
    // ======================================

    L.control.scale({

        imperial: false,

        metric: true,

        position: "bottomleft"

    }).addTo(fraMap);


    // ======================================
    // 7. RESET MAP FUNCTION
    // ======================================

    window.resetMapView = function () {

        fraMap.flyTo(

            odishaCenter,

            initialZoom,

            {

                animate: true,

                duration: 1.2

            }

        );

    };


    // ======================================
    // 8. MAP RESIZE HANDLING
    // ======================================

    function refreshMapSize() {

        fraMap.invalidateSize({

            animate: false,

            pan: false

        });

    }


    // Refresh map after page rendering
    setTimeout(function () {

        refreshMapSize();

        fraMap.setView(
            odishaCenter,
            initialZoom
        );

    }, 500);


    // Refresh after browser resize
    window.addEventListener(
        "resize",
        refreshMapSize
    );


    // ======================================
    // 9. HANDLE CONTAINER RESIZING
    // ======================================

    if (typeof ResizeObserver !== "undefined") {

        const resizeObserver = new ResizeObserver(function () {

            refreshMapSize();

        });

        resizeObserver.observe(mapElement);

    }


    // ======================================
    // 10. MAP INITIALIZATION COMPLETE
    // ======================================

    console.log(
        "Odisha FRA WebGIS map initialized successfully."
    );

    console.log(
        "Map Centre:",
        odishaCenter
    );

    console.log(
        "Initial Zoom:",
        initialZoom
    );

});
