window.ExperienceList = (() => {
    "use strict";

    const page = document.getElementById("experience");

    if (!page) return null;

    const grid = document.getElementById("experience-grid");
    const empty = document.getElementById("experience-empty");
    const retry = document.getElementById("experience-retry");
    const csrfSource = document.querySelector(
        "#experience-csrf-source input[name='csrfmiddlewaretoken']"
    );

    const placeholderId = "00000000-0000-0000-0000-000000000000";

    let activeController = null;

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

        cancel();

        const controller = new AbortController();
        activeController = controller;

        showSection("loading");

        try {
            const url = new URL(
                page.dataset.listUrl,
                location.origin
            );

            if (searchQuery) {
                url.searchParams.set("title", searchQuery);
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

            empty.textContent = searchQuery
                ? "Tidak ada pengalaman yang cocok dengan pencarian."
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
        if (action === "delete" && !window.confirm("Hapus experience ini?")) {
            return;
        }

        button.disabled = true;
        try {
            const pattern = action === "star"
                ? page.dataset.starUrl
                : page.dataset.deleteUrl;
            await window.ExperienceAPI.write(
                route(pattern, button.dataset.id),
                action === "star" ? "POST" : "DELETE",
                undefined,
                csrfSource?.value
            );
            window.showToast(
                "Berhasil",
                action === "star"
                    ? "Status star diperbarui."
                    : "Experience berhasil dihapus.",
                "success"
            );
            await load();
        } catch (error) {
            window.showToast("Permintaan gagal", error.message, "error", 7000);
        } finally {
            button.disabled = false;
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
