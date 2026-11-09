(() => {
    "use strict";

    const list = window.ExperienceList;
    const form = document.getElementById("experience-search-form");
    const input = document.getElementById("experience-search");
    const reset = document.getElementById("experience-search-reset");
    const filters = [
        document.getElementById("experience-category"),
        document.getElementById("experience-status"),
    ].filter(Boolean);

    if (!list || !form || !input || !reset) return;

    const DEBOUNCE_DELAY = 300;
    let timer = null;

    function clearPendingSearch() {
        clearTimeout(timer);
        timer = null;
    }

    function search() {
        clearPendingSearch();
        list.load(input.value.trim());
    }

    input.addEventListener("input", () => {
        clearPendingSearch();
        list.cancel();

        timer = setTimeout(search, DEBOUNCE_DELAY);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        search();
    });

    filters.forEach((filter) => filter.addEventListener("change", search));

    reset.addEventListener("click", () => {
        clearPendingSearch();
        input.value = "";
        filters.forEach((filter) => { filter.value = ""; });
        list.load("");
        input.focus();
    });

    for (const event of ["experience:created", "experience:updated"]) {
        document.addEventListener(event, () => {
            clearPendingSearch();
            list.load(input.value.trim());
        });
    }
})();
