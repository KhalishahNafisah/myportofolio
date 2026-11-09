(() => {
    "use strict";

    const page = document.getElementById("experience");
    const dialog = document.getElementById("edit-experience-dialog");
    const form = document.getElementById("experience-edit-form");
    if (!page || !dialog || !form) return;

    const loading = document.getElementById("edit-experience-loading");
    const errorMessage = document.getElementById("edit-experience-error");
    const retry = document.getElementById("edit-experience-retry");
    const submit = form.querySelector('button[type="submit"]');
    const fields = form.querySelector("fieldset");
    const closeButtons = dialog.querySelectorAll("[data-close-edit]");
    let controller = null;
    let endpoint = "";
    let initialPayload = {};
    let saving = false;

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.hidden = false;
        window.showToast("Permintaan gagal", message, "error", 7000);
    }

    async function loadExperience() {
        controller?.abort();
        const current = new AbortController();
        controller = current;
        form.reset();
        dialog.scrollTop = 0;
        form.hidden = true;
        loading.hidden = false;
        errorMessage.hidden = true;
        retry.hidden = true;
        dialog.setAttribute("aria-busy", "true");

        try {
            const response = await fetch(endpoint, {
                headers: { Accept: "application/json" },
                credentials: "same-origin",
                cache: "no-store",
                signal: current.signal,
            });
            const experience = await response.json();
            if (current.signal.aborted) return;
            if (!response.ok) {
                throw new Error(response.status === 404
                    ? "Experience ini sudah tidak tersedia. Muat ulang daftar."
                    : experience.detail || `Gagal memuat experience (HTTP ${response.status}).`);
            }

            for (const name of ["title", "description", "category", "thumbnail"]) {
                form.elements.namedItem(name).value = experience[name] ?? "";
            }
            form.elements.namedItem("ended_at").value = experience.ended_at
                ? new Date(experience.ended_at).toISOString().slice(0, 16)
                : "";
            initialPayload = window.ExperienceAPI.formPayload(form);
            form.hidden = false;
            form.elements.namedItem("title").focus({ preventScroll: true });
        } catch (error) {
            if (current.signal.aborted) return;
            showError(error instanceof TypeError
                ? "Experience belum dapat dimuat. Periksa koneksi lalu coba lagi."
                : error.message);
            retry.hidden = false;
        } finally {
            if (controller === current) {
                controller = null;
                loading.hidden = true;
                dialog.removeAttribute("aria-busy");
            }
        }
    }

    document.getElementById("experience-grid").addEventListener("click", (event) => {
        const link = event.target.closest('a[data-action="edit"]');
        if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        endpoint = page.dataset.editApiUrl.replace(
            "00000000-0000-0000-0000-000000000000",
            encodeURIComponent(link.dataset.id)
        );
        dialog.showModal();
        loadExperience();
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (!saving) dialog.close();
        });
    });
    dialog.addEventListener("cancel", (event) => {
        if (saving) event.preventDefault();
    });
    dialog.addEventListener("close", () => {
        controller?.abort();
        controller = null;
        dialog.removeAttribute("aria-busy");
        form.reset();
        form.hidden = true;
    });
    retry.addEventListener("click", loadExperience);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (saving || controller || form.hidden) return;
        errorMessage.hidden = true;

        const payload = Object.fromEntries(
            Object.entries(window.ExperienceAPI.formPayload(form))
                .filter(([name, value]) => value !== initialPayload[name])
        );
        if (!Object.keys(payload).length) {
            window.showToast("Belum ada perubahan", "Ubah data yang ingin diperbarui terlebih dahulu.");
            return;
        }

        saving = true;
        fields.disabled = true;
        submit.disabled = true;
        closeButtons.forEach((button) => { button.disabled = true; });
        submit.textContent = "Menyimpan...";
        dialog.setAttribute("aria-busy", "true");
        errorMessage.hidden = true;

        try {
            await window.ExperienceAPI.write(
                endpoint,
                "PATCH",
                payload,
                form.elements.namedItem("csrfmiddlewaretoken").value
            );
            dialog.close();
            window.showToast("Berhasil", "Experience berhasil diperbarui.", "success", 4000);
            document.dispatchEvent(new Event("experience:updated"));
            document.getElementById("experience-search")?.focus();
        } catch (error) {
            showError(error instanceof TypeError
                ? "Koneksi terputus saat menyimpan. Periksa daftar sebelum mengirim ulang."
                : error.message);
        } finally {
            saving = false;
            fields.disabled = false;
            submit.disabled = false;
            closeButtons.forEach((button) => { button.disabled = false; });
            submit.textContent = "Simpan perubahan";
            dialog.removeAttribute("aria-busy");
        }
    });
})();
