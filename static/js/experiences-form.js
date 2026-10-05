(() => {
    "use strict";

    const form = document.getElementById("experience-form");
    const modal = document.getElementById("add-experience-modal");

    if (!form || !modal) return;

    const submitButton = form.querySelector(
        'button[type="submit"]'
    );

    if (!submitButton) return;

    function validationMessage(result, status) {
        if (result.errors) {
            const messages = Object.values(result.errors)
                .flat()
                .map((error) => error.message)
                .filter(Boolean);

            if (messages.length) {
                return messages.join(" ");
            }
        }

        return result.message ||
            `Permintaan gagal (HTTP ${status}). Silakan coba lagi.`;
    }

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

            const response = await fetch(form.dataset.ajaxUrl, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "X-CSRFToken": csrfInput.value,
                },
                body: new FormData(form),
                credentials: "same-origin",
            });

            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                showToast(
                    "Gagal menyimpan",
                    validationMessage(result, response.status),
                    "error",
                    7000
                );

                return;
            }

            form.reset();

            if (modal.matches(":popover-open")) {
                modal.hidePopover();
            }

            showToast(
                "Berhasil",
                result.message || "Experience berhasil ditambahkan.",
                "success",
                4000
            );

            document.dispatchEvent(
                new Event("experience:created")
            );
        } catch (error) {
            console.error("Gagal menyimpan Experience:", error);

            showToast(
                "Permintaan gagal",
                "Periksa koneksi. Jika koneksi terputus saat menyimpan, periksa daftar sebelum mengirim ulang.",
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
