window.ExperienceList = (() => {
    "use strict";

    const page = document.getElementById("experience");

    if (!page) return null;

    const grid = document.getElementById("experience-grid");
    const empty = document.getElementById("experience-empty");
    const retry = document.getElementById("experience-retry");
    const results = document.getElementById("experience-results");
    const csrfSource = document.querySelector(
        "#experience-csrf-source input[name='csrfmiddlewaretoken']"
    );
    const deleteDialog = document.getElementById("delete-experience-dialog");
    const deleteTitle = document.getElementById("delete-experience-title");
    const deleteError = document.getElementById("delete-experience-error");
    const confirmDelete = document.getElementById("confirm-delete-experience");
    const cancelDelete = document.getElementById("cancel-delete-experience");

    const placeholderId = "00000000-0000-0000-0000-000000000000";

    let activeController = null;
    let pendingDelete = null;
    let deleting = false;

    function element(tag, className = "", text = null) {
        const node = document.createElement(tag);

        if (className) {
            node.className = className;
        }

        if (text !== null) {
            node.textContent = String(text);
        }

        return node;
    }

    function route(template, id) {
        return template.replace(
            placeholderId,
            encodeURIComponent(String(id))
        );
    }

    function safeHttpUrl(value) {
        if (!value) return "";

        try {
            const url = new URL(value);

            return ["http:", "https:"].includes(url.protocol)
                ? url.href
                : "";
        } catch {
            return "";
        }
    }

    function showSection(name) {
        results?.classList.toggle("hide", name === "loading" || name === "error");
        for (const section of ["loading", "error", "empty", "grid"]) {
            document
                .getElementById(`experience-${section}`)
                .classList
                .toggle("hide", section !== name);
        }

        grid.setAttribute(
            "aria-busy",
            name === "loading" ? "true" : "false"
        );
    }

    function buildStarControl(experience) {
        const count = element(
            "span",
            "star-count",
            experience.star_count
        );

        if (page.dataset.authenticated !== "true") {
            const login = element(
                "a",
                "button button-star",
                "Login to star ★ "
            );

            const loginUrl = new URL(
                page.dataset.loginUrl,
                location.origin
            );

            loginUrl.searchParams.set(
                "next",
                location.pathname + location.search
            );

            login.href = loginUrl.href;
            login.append(count);

            return login;
        }

        const isStarred = Boolean(experience.is_starred);

        const button = element(
            "button",
            `button button-star${isStarred ? " is-starred" : ""}`,
            `★ ${isStarred ? "Unstar" : "Star"} `
        );

        button.type = "button";
        button.dataset.action = "star";
        button.dataset.id = experience.id;
        button.setAttribute(
            "aria-pressed",
            isStarred ? "true" : "false"
        );

        button.setAttribute(
            "aria-label",
            `${isStarred ? "Batalkan star" : "Beri star"} untuk ${experience.title}`
        );

        button.append(count);
        return button;
    }

    function buildCard(experience) {
        const article = element("article", "experience-card");

        const imageUrl = safeHttpUrl(experience.thumbnail);

        if (imageUrl) {
            const image = element("img", "portfolio-project-image");
            image.src = imageUrl;
            image.alt = String(experience.title ?? "");
            image.loading = "lazy";
            article.append(image);
        }

        article.append(
            element(
                "span",
                "experience-category",
                experience.category_display
            )
        );

        const heading = element("h2");
        const detailLink = element("a", "", experience.title);

        detailLink.href = route(page.dataset.detailUrl, experience.id);
        heading.append(detailLink);
        article.append(heading);

        article.append(
            element(
                "p",
                "experience-description",
                experience.description
            )
        );

        article.append(
            element(
                "p",
                "experience-status",
                experience.is_ongoing
                    ? "Sedang berlangsung"
                    : "Selesai"
            )
        );

        const actions = element("div", "portfolio-actions");
        actions.append(buildStarControl(experience));

        if (page.dataset.editUrl) {
            const edit = element(
                "a",
                "button button-secondary",
                "Edit"
            );

            edit.href = route(page.dataset.editUrl, experience.id);
            edit.dataset.action = "edit";
            edit.dataset.id = experience.id;
            edit.setAttribute("aria-haspopup", "dialog");
            edit.setAttribute("aria-controls", "edit-experience-dialog");
            actions.append(edit);
        }

        if (page.dataset.deleteUrl) {
            const button = element(
                "button",
                "button button-danger",
                "Hapus"
            );

            button.type = "button";
            button.dataset.action = "delete";
            button.dataset.id = experience.id;
            button.setAttribute("aria-haspopup", "dialog");
            button.setAttribute("aria-controls", "delete-experience-dialog");
            actions.append(button);
        }

        article.append(actions);

        return article;
    }

    function cancel() {
        if (activeController) {
            activeController.abort();
            activeController = null;
        }
    }

    async function load(query) {
        const input = document.getElementById("experience-search");

        const searchQuery = (
            query === undefined
                ? input?.value ?? ""
                : query
        ).trim();
        const category = document.getElementById("experience-category")?.value ?? "";
        const status = document.getElementById("experience-status")?.value ?? "";

        const pageUrl = new URL(location.href);
        for (const [key, value] of Object.entries({ title: searchQuery, category, status })) {
            if (value) pageUrl.searchParams.set(key, value);
            else pageUrl.searchParams.delete(key);
        }
        if (pageUrl.href !== location.href) {
            history.replaceState(null, "", pageUrl);
        }

        cancel();

        const controller = new AbortController();
        activeController = controller;

        showSection("loading");

        try {
            const url = new URL(
                page.dataset.listUrl,
                location.origin
            );

            for (const [key, value] of Object.entries({ title: searchQuery, category, status })) {
                if (value) url.searchParams.set(key, value);
            }

            const response = await fetch(url, {
                headers: {
                    Accept: "application/json",
                },
                credentials: "same-origin",
                cache: "no-store",
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const items = await response.json();

            if (controller.signal.aborted) return;

            if (!Array.isArray(items)) {
                throw new Error("Format respons daftar tidak sesuai.");
            }

            const cards = items.map(buildCard);
            grid.replaceChildren(...cards);
            if (results) results.textContent = `Menampilkan ${items.length} pengalaman`;

            empty.textContent = searchQuery || category || status
                ? "Tidak ada pengalaman yang cocok dengan pencarian atau filter ini."
                : "Belum ada pengalaman yang ditambahkan.";

            showSection(items.length ? "grid" : "empty");
        } catch (error) {
            if (
                error.name === "AbortError" ||
                controller.signal.aborted
            ) {
                return;
            }

            console.error("Gagal memuat Experience:", error);
            showSection("error");

            if (typeof window.showToast === "function") {
                window.showToast(
                    "Gagal memuat",
                    "Daftar pengalaman belum dapat dimuat. Silakan coba lagi.",
                    "error",
                    5000
                );
            }
        } finally {
            if (activeController === controller) {
                activeController = null;
            }
        }
    }

    grid.addEventListener("click", async (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button || button.disabled) return;

        const action = button.dataset.action;
        if (!["star", "delete"].includes(action)) return;

        if (action === "delete") {
            if (!deleteDialog || deleting) return;
            pendingDelete = button;
            deleteTitle.textContent = button.closest("article").querySelector("h2").textContent;
            deleteError.hidden = true;
            deleteDialog.showModal();
            return;
        }

        button.disabled = true;
        try {
            await window.ExperienceAPI.write(
                route(page.dataset.starUrl, button.dataset.id),
                "POST",
                undefined,
                csrfSource?.value
            );
            window.showToast(
                "Berhasil",
                "Status star diperbarui.",
                "success"
            );
            await load();
        } catch (error) {
            window.showToast("Permintaan gagal", error.message, "error", 7000);
        } finally {
            button.disabled = false;
        }
    });

    deleteDialog?.addEventListener("cancel", (event) => {
        if (deleting) event.preventDefault();
    });

    deleteDialog?.addEventListener("close", () => {
        pendingDelete = null;
        deleteError.textContent = "";
        deleteError.hidden = true;
    });

    confirmDelete?.addEventListener("click", async () => {
        if (!pendingDelete || deleting) return;

        const button = pendingDelete;
        deleting = true;
        button.disabled = true;
        confirmDelete.disabled = true;
        cancelDelete.disabled = true;
        confirmDelete.textContent = "Menghapus...";
        deleteDialog.setAttribute("aria-busy", "true");
        deleteError.hidden = true;

        try {
            await window.ExperienceAPI.write(
                route(page.dataset.deleteUrl, button.dataset.id),
                "DELETE",
                undefined,
                csrfSource?.value
            );
            deleteDialog.close();
            window.showToast("Berhasil", "Experience berhasil dihapus.", "success");
            await load();
            document.getElementById("experience-search")?.focus();
        } catch (error) {
            deleteError.textContent = error instanceof TypeError
                ? "Koneksi terputus. Periksa daftar sebelum mencoba menghapus kembali."
                : error.message;
            deleteError.hidden = false;
            window.showToast("Gagal menghapus", deleteError.textContent, "error", 7000);
        } finally {
            deleting = false;
            button.disabled = false;
            confirmDelete.disabled = false;
            cancelDelete.disabled = false;
            confirmDelete.textContent = "Ya, hapus";
            deleteDialog.removeAttribute("aria-busy");
        }
    });

    if (retry) {
        retry.addEventListener("click", () => load());
    }

    load();

    return {
        load,
        cancel,
    };
})();
