
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // 1. DOM ELEMENTS
    // =====================================

    const searchInput = document.getElementById("villageSearchInput");
    const suggestionsBox = document.getElementById("villageSuggestions");
    const selectedVillageId = document.getElementById("selectedVillageId");

    const districtFilter = document.getElementById("districtFilter");
    const blockFilter = document.getElementById("blockFilter");
    const gpFilter = document.getElementById("gpFilter");

    const clearButton = document.getElementById("clearVillageSearch");
    const searchForm = document.getElementById("villageSearchForm");

    if (!searchInput || !suggestionsBox) return;

    const villageApi = window.VILLAGE_API_URL;
    const blockApi = window.BLOCK_API_URL;
    const gpApi = window.GP_API_URL;

    let debounceTimer = null;
    let activeSuggestions = [];
    let requestNumber = 0;
    let selectedVillage = false;

    // =====================================
    // 2. HIDE SUGGESTIONS
    // =====================================

    function hideSuggestions() {
        suggestionsBox.hidden = true;
        suggestionsBox.innerHTML = "";
        activeSuggestions = [];
    }

    // =====================================
    // 3. CLEAR SELECTED VILLAGE
    // =====================================

    function clearSelectedVillage() {
        if (selectedVillageId) {
            selectedVillageId.value = "";
        }

        selectedVillage = false;
    }

    // =====================================
    // 4. LOAD DROPDOWN OPTIONS
    // =====================================

    async function populateDropdown(
        selectElement,
        url,
        placeholder,
        selectedValue = ""
    ) {
        if (!selectElement) return;

        selectElement.disabled = true;
        selectElement.innerHTML = "";

        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = placeholder;

        selectElement.appendChild(defaultOption);

        if (!url) {
            selectElement.disabled = false;
            return;
        }

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error("Unable to load dropdown options");
            }

            const items = await response.json();

            items.forEach(item => {
                const option = document.createElement("option");

                option.value = item;
                option.textContent = item;

                if (
                    String(item).toUpperCase() ===
                    String(selectedValue).toUpperCase()
                ) {
                    option.selected = true;
                }

                selectElement.appendChild(option);
            });

        } catch (error) {
            console.error("Dropdown error:", error);

        } finally {
            selectElement.disabled = false;
        }
    }

    // =====================================
    // 5. VILLAGE AUTOCOMPLETE API
    // =====================================

    async function searchVillages(query = "") {

        if (!villageApi) {
            console.error("Village API URL is missing.");
            return [];
        }

        const currentRequest = ++requestNumber;

        const params = new URLSearchParams();
        params.set("q", query);

        if (districtFilter) {
            params.set("district", districtFilter.value);
        }

        if (blockFilter) {
            params.set("block", blockFilter.value);
        }

        if (gpFilter) {
            params.set("gp", gpFilter.value);
        }

        try {
            const response = await fetch(
                `${villageApi}?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error("Village search failed");
            }

            const results = await response.json();

            if (currentRequest !== requestNumber) {
                return [];
            }

            renderSuggestions(results);

            return results;

        } catch (error) {
            console.error("Village search error:", error);
            hideSuggestions();
            return [];
        }
    }

    // =====================================
    // 6. DISPLAY VILLAGE SUGGESTIONS
    // =====================================

    function renderSuggestions(items) {

        suggestionsBox.innerHTML = "";
        activeSuggestions = items || [];

        if (!activeSuggestions.length) {

            const emptyMessage = document.createElement("div");

            emptyMessage.className = "suggestion-empty";
            emptyMessage.textContent = "No villages found.";

            suggestionsBox.appendChild(emptyMessage);
            suggestionsBox.hidden = false;

            return;
        }

        activeSuggestions.forEach(item => {

            const option = document.createElement("button");

            option.type = "button";
            option.className = "village-suggestion-item";
            option.setAttribute("role", "option");

            const icon = document.createElement("span");

            icon.className = "suggestion-icon";
            icon.textContent = "📍";

            const details = document.createElement("span");

            details.className = "suggestion-details";

            const villageName = document.createElement("strong");

            villageName.textContent = item.village || "";

            const location = document.createElement("small");

            location.textContent =
                `${item.gp || ""} | ${item.block || ""} | ${item.district || ""}`;

            details.appendChild(villageName);
            details.appendChild(location);

            option.appendChild(icon);
            option.appendChild(details);

            option.addEventListener("click", () => {
                selectVillage(item);
            });

            suggestionsBox.appendChild(option);
        });

        suggestionsBox.hidden = false;
    }

    // =====================================
    // 7. SELECT VILLAGE
    // =====================================

    async function selectVillage(item) {

        clearTimeout(debounceTimer);

        clearSelectedVillage();

        if (selectedVillageId) {
            selectedVillageId.value = item.id;
        }

        searchInput.value = item.village || "";

        selectedVillage = true;

        hideSuggestions();

        if (districtFilter) {
            districtFilter.value = item.district || "";
        }

        if (blockFilter) {

            await populateDropdown(
                blockFilter,
                blockApi
                    ? `${blockApi}?district=${encodeURIComponent(item.district)}`
                    : null,
                "All Blocks",
                item.block
            );
        }

        if (gpFilter) {

            await populateDropdown(
                gpFilter,
                gpApi
                    ? `${gpApi}?district=${encodeURIComponent(item.district)}&block=${encodeURIComponent(item.block)}`
                    : null,
                "All Gram Panchayats",
                item.gp
            );
        }
    }

    // =====================================
    // 8. RESTORE SELECTED VILLAGE ON PAGE LOAD
    // =====================================

    async function restoreSelectedVillage() {

        const urlParams = new URLSearchParams(window.location.search);

        const villageId = urlParams.get("village_id");
        const district = urlParams.get("district") || "";
        const block = urlParams.get("block") || "";
        const gp = urlParams.get("gp") || "";

        if (!villageId) return;

        // Restore district
        if (districtFilter && district) {
            districtFilter.value = district;
        }

        // Restore block dropdown
        if (blockFilter && district) {

            await populateDropdown(
                blockFilter,
                blockApi
                    ? `${blockApi}?district=${encodeURIComponent(district)}`
                    : null,
                "All Blocks",
                block
            );
        }

        // Restore Gram Panchayat dropdown
        if (gpFilter && district && block) {

            await populateDropdown(
                gpFilter,
                gpApi
                    ? `${gpApi}?district=${encodeURIComponent(district)}&block=${encodeURIComponent(block)}`
                    : null,
                "All Gram Panchayats",
                gp
            );
        }

        // Search within selected administrative location
        const results = await searchVillages("");

        // Find the exact village using its ID
        const matchedVillage = results.find(item =>
            String(item.id) === String(villageId)
        );

        if (matchedVillage) {

            // Restore name and selected village ID
            searchInput.value = matchedVillage.village || "";

            if (selectedVillageId) {
                selectedVillageId.value = matchedVillage.id;
            }

            selectedVillage = true;
            hideSuggestions();

        } else {

            console.warn(
                "Selected village was not found in autocomplete results. Check the API result limit or add an API lookup by village_id."
            );
        }
    }

    // =====================================
    // 9. INPUT FOCUS
    // =====================================

    searchInput.addEventListener("focus", () => {

        clearTimeout(debounceTimer);

        searchVillages(searchInput.value.trim());
    });

    // =====================================
    // 10. SEARCH WHILE TYPING
    // =====================================

    searchInput.addEventListener("input", () => {

        clearSelectedVillage();

        clearTimeout(debounceTimer);

        const query = searchInput.value.trim();

        debounceTimer = setTimeout(() => {
            searchVillages(query);
        }, 250);
    });

    // =====================================
    // 11. CLEAR VILLAGE SEARCH
    // =====================================

    if (clearButton) {

        clearButton.addEventListener("click", () => {

            searchInput.value = "";

            clearSelectedVillage();

            hideSuggestions();

            searchInput.focus();

            searchVillages("");
        });
    }

    // =====================================
    // 12. DISTRICT CHANGE
    // =====================================

    if (districtFilter) {

        districtFilter.addEventListener("change", async () => {

            clearSelectedVillage();

            searchInput.value = "";

            hideSuggestions();

            if (blockFilter) blockFilter.value = "";
            if (gpFilter) gpFilter.value = "";

            const district = districtFilter.value;

            await populateDropdown(
                blockFilter,
                district && blockApi
                    ? `${blockApi}?district=${encodeURIComponent(district)}`
                    : null,
                "All Blocks"
            );

            await populateDropdown(
                gpFilter,
                null,
                "All Gram Panchayats"
            );
        });
    }

    // =====================================
    // 13. BLOCK CHANGE
    // =====================================

    if (blockFilter) {

        blockFilter.addEventListener("change", async () => {

            clearSelectedVillage();

            searchInput.value = "";

            hideSuggestions();

            if (gpFilter) gpFilter.value = "";

            const district = districtFilter
                ? districtFilter.value
                : "";

            const block = blockFilter.value;

            const url = district && block && gpApi
                ? `${gpApi}?district=${encodeURIComponent(district)}&block=${encodeURIComponent(block)}`
                : null;

            await populateDropdown(
                gpFilter,
                url,
                "All Gram Panchayats"
            );
        });
    }

    // =====================================
    // 14. GRAM PANCHAYAT CHANGE
    // =====================================

    if (gpFilter) {

        gpFilter.addEventListener("change", () => {

            clearSelectedVillage();

            searchInput.value = "";

            hideSuggestions();
        });
    }

    // =====================================
    // 15. CLICK OUTSIDE
    // =====================================

    document.addEventListener("click", event => {

        if (!event.target.closest(".village-autocomplete")) {
            hideSuggestions();
        }
    });

    // =====================================
    // 16. KEYBOARD SUPPORT
    // =====================================

    searchInput.addEventListener("keydown", event => {

        if (event.key === "Escape") {
            hideSuggestions();
        }

        if (
            event.key === "Enter" &&
            !suggestionsBox.hidden &&
            activeSuggestions.length > 0
        ) {

            event.preventDefault();

            selectVillage(activeSuggestions[0]);
        }
    });

    // =====================================
    // 17. FORM VALIDATION
    // =====================================

    if (searchForm) {

        searchForm.addEventListener("submit", event => {

            const typedValue = searchInput.value.trim();

            if (typedValue && !selectedVillageId?.value) {

                event.preventDefault();

                alert(
                    "Please select a village from the suggestions."
                );

                searchInput.focus();

                searchVillages(typedValue);
            }
        });
    }

    // =====================================
    // 18. INITIALIZATION
    // =====================================

    restoreSelectedVillage();

    console.log("Village Explorer initialized successfully.");

});
