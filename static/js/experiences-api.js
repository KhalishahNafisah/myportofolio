window.ExperienceAPI = (() => {
    "use strict";

    function formPayload(form) {
        const fields = new FormData(form);
        const endedAt = String(fields.get("ended_at") ?? "").trim();
        const payload = Object.fromEntries([
            "title", "description", "category", "thumbnail",
        ].map((name) => [name, fields.get(name)]));

        // The existing datetime-local input is explicitly labelled as UTC.
        payload.ended_at = endedAt ? `${endedAt}Z` : null;
        return payload;
    }

    function errorMessage(data, status) {
        const messages = Object.values(data ?? {})
            .flat()
            .filter((value) => typeof value === "string");

        return messages.join(" ") || `Permintaan gagal (HTTP ${status}).`;
    }

    async function write(url, method, payload, csrfToken) {
        if (!csrfToken) {
            throw new Error("Token CSRF tidak ditemukan. Muat ulang halaman.");
        }

        const response = await fetch(url, {
            method,
            credentials: "same-origin",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });

        if (response.status === 204) return null;

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(errorMessage(data, response.status));
        }
        return data;
    }

    return { formPayload, write };
})();
