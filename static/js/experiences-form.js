(() => {
    "use strict";

    const form = document.getElementById("experience-form");
    const modal = document.getElementById("add-experience-modal");

    if (!form) return;

    const submitButton = form.querySelector(
        'button[type="submit"]'
    );

    if (!submitButton) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (submitButton.disabled) return;

        const initialText = submitButton.textContent;

        submitButton.disabled = true;
        submitButton.textContent = "Menyimpan...";
        form.setAttribute("aria-busy", "true");

        try {
            const csrfInput = form.querySelector(
                '[name="csrfmiddlewaretoken"]'
            );

            if (!csrfInput) {
                throw new Error("Token CSRF tidak ditemukan.");
            }

            const method = form.dataset.apiMethod || "POST";
            await window.ExperienceAPI.write(
                form.dataset.ajaxUrl,
                method,
                window.ExperienceAPI.formPayload(form),
                csrfInput.value
            );

            if (method === "POST") form.reset();

            if (modal?.matches(":popover-open")) {
                modal.hidePopover();
            }

            showToast(
                "Berhasil",
                method === "PATCH"
                    ? "Experience berhasil diperbarui."
                    : "Experience berhasil ditambahkan.",
                "success",
                4000
            );

            if (method === "POST") {
                document.dispatchEvent(new Event("experience:created"));
            }
        } catch (error) {
            console.error("Gagal menyimpan Experience:", error);

            showToast(
                "Permintaan gagal",
                error instanceof TypeError
                    ? "Periksa koneksi. Jika koneksi terputus saat menyimpan, periksa daftar sebelum mengirim ulang."
                    : error.message,
                "error",
                7000
            );
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = initialText;
            form.removeAttribute("aria-busy");
        }
    });
})();
