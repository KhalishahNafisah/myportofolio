(() => {
    "use strict";

    const list = window.ExperienceList;
    const form = document.getElementById("experience-search-form");
    const input = document.getElementById("experience-search");
    const reset = document.getElementById("experience-search-reset");

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

    reset.addEventListener("click", () => {
        clearPendingSearch();
        input.value = "";
        list.load("");
        input.focus();
    });

    document.addEventListener("experience:created", () => {
        clearPendingSearch();
        input.value = "";
        list.load("");
    });
})();
