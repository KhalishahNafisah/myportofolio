const projectsPage = document.getElementById("projects");
const searchForm = document.getElementById("project-search-form");
const searchInput = document.getElementById("search-input");
const grid = document.getElementById("grid");

const placeholderId = "00000000-0000-0000-0000-000000000000";

let projectsAbortController;
const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;

function getCsrfToken() {
    return document.querySelector(
        "#csrf-source input[name='csrfmiddlewaretoken']"
    )?.value ?? "";
}

function projectEndpoint(pattern, id) {
    return pattern.replace(
        placeholderId,
        encodeURIComponent(String(id))
    );
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function safeHttpUrl(value) {
    try {
        const url = new URL(value);

        return ["http:", "https:"].includes(url.protocol)
            ? url.href
            : "";
    } catch {
        return "";
    }
}

function displayPageSection(section) {
    for (const id of ["loading", "error", "empty", "grid"]) {
        document
            .getElementById(id)
            .classList
            .toggle("hide", id !== section);
    }
}

function buildProjectCardElement(project) {
    const article = document.createElement("article");
    article.className = "experience-card";

    const route = (template) => {
        return escapeHtml(
            projectEndpoint(template, project.id)
        );
    };

    const imageUrl = safeHttpUrl(project.project_image_url);
    const projectUrl = safeHttpUrl(project.project_url);
    const count = escapeHtml(project.star_count);

    const imageHtml = imageUrl
        ? `
            <img
                class="portfolio-project-image"
                src="${escapeHtml(imageUrl)}"
                alt="${escapeHtml(project.title)}"
                loading="lazy"
            >
        `
        : "";

    const linkHtml = projectUrl
        ? `
            <a
                class="social-link"
                href="${escapeHtml(projectUrl)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                View Project
            </a>
        `
        : "";

    const loginUrl =
        `${projectsPage.dataset.loginUrl}?next=` +
        encodeURIComponent(location.pathname + location.search);

    const starHtml = projectsPage.dataset.authenticated === "true"
        ? `
            <button
                type="button"
                class="button button-star${project.is_starred ? " is-starred" : ""}"
                data-action="star"
                data-id="${escapeHtml(project.id)}"
                aria-pressed="${project.is_starred ? "true" : "false"}"
            >
                ★ ${project.is_starred ? "Unstar" : "Star"}

                <span class="star-count">${count}</span>
            </button>
        `
        : `
            <a
                class="button button-star"
                href="${escapeHtml(loginUrl)}"
            >
                Login to star ★
                <span class="star-count">${count}</span>
            </a>
        `;

    const editHtml = projectsPage.dataset.editUrl
        ? `
            <a
                class="button button-secondary"
                href="${route(projectsPage.dataset.editUrl)}"
            >
                Edit
            </a>
        `
        : "";

    const deleteHtml = projectsPage.dataset.deleteUrl
        ? `
            <button
                type="button"
                class="button button-danger"
                data-action="delete"
                data-id="${escapeHtml(project.id)}"
            >
                Hapus
            </button>
        `
        : "";

    article.innerHTML = `
        ${imageHtml}

        <span class="experience-category">
            ${escapeHtml(project.category_display)}
        </span>

        <h2>${escapeHtml(project.title)}</h2>

        <p class="experience-description">
            ${escapeHtml(project.description)}
        </p>

        <p class="experience-status">
            ${escapeHtml(project.year)}
        </p>

        ${linkHtml}

        <div class="portfolio-actions">
            ${starHtml}
            ${editHtml}
            ${deleteHtml}
        </div>
    `;

    return article;
}

async function fetchProjects(query = "") {
    if (projectsAbortController) {
        projectsAbortController.abort();
    }

    const controller = new AbortController();
    projectsAbortController = controller;

    displayPageSection("loading");

    try {
        const url = new URL(
            projectsPage.dataset.listUrl,
            location.origin
        );

        if (query) {
            url.searchParams.set("title", query);
        }

        const response = await fetch(url, {
            headers: {
                Accept: "application/json",
            },
            credentials: "same-origin",
            signal: controller.signal,
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const items = await response.json();

        if (controller.signal.aborted) return;

        if (!Array.isArray(items)) {
            throw new Error("Format daftar proyek tidak sesuai.");
        }

        grid.replaceChildren(
            ...items.map(buildProjectCardElement)
        );

        document.getElementById("empty").textContent = query
            ? "No matching projects found."
            : "No projects have been added yet.";

        displayPageSection(items.length ? "grid" : "empty");
    } catch (error) {
        if (error.name === "AbortError" || controller.signal.aborted) return;

        console.error(error);
        displayPageSection("error");
    }
}

function searchProjects() {
    fetchProjects(searchInput.value.trim());
}

searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);

    if (projectsAbortController) {
        projectsAbortController.abort();
    }

    searchDebounceTimer = setTimeout(
        searchProjects,
        SEARCH_DEBOUNCE_DELAY
    );
});

searchForm.addEventListener("submit", (event) => {
    event.preventDefault();

    clearTimeout(searchDebounceTimer);
    searchProjects();
});

document.getElementById("reset-search").addEventListener("click", () => {
    clearTimeout(searchDebounceTimer);

    searchInput.value = "";
    searchProjects();
});

document
    .getElementById("retry-projects")
    .addEventListener("click", searchProjects);

const projectForm = document.getElementById("project-form");

function closeProjectModal() {
    document
        .getElementById("add-project-modal")
        .hidePopover();
}

function apiErrorMessage(data, status) {
    const messages = Object.values(data ?? {})
        .flat()
        .filter((value) => typeof value === "string");

    return messages.join(" ") ||
        `Permintaan gagal (HTTP ${status}).`;
}

async function writeProject(url, method, payload) {
    const response = await fetch(url, {
        method,
        credentials: "same-origin",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: payload === undefined
            ? undefined
            : JSON.stringify(payload),
    });

    if (response.status === 204) return null;

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(apiErrorMessage(result, response.status));
    }

    return result;
}

async function addProject(event) {
    event.preventDefault();

    const button = projectForm.querySelector(
        'button[type="submit"]'
    );

    if (button.disabled) return;

    button.disabled = true;

    try {
        const fields = new FormData(projectForm);
        const payload = Object.fromEntries([
            "title",
            "description",
            "category",
            "year",
            "project_url",
            "project_image_url",
        ].map((name) => [name, fields.get(name)]));

        await writeProject(
            projectForm.dataset.ajaxUrl,
            "POST",
            payload
        );

        projectForm.reset();
        closeProjectModal();

        showToast(
            "Berhasil",
            "Proyek berhasil ditambahkan.",
            "success"
        );

        await fetchProjects(searchInput.value.trim());
    } catch (error) {
        console.error(error);

        showToast(
            "Gagal menyimpan",
            error.message,
            "error",
            6000
        );
    } finally {
        button.disabled = false;
    }
}

if (projectForm) {
    projectForm.addEventListener("submit", addProject);
}

grid.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");

    if (!button || button.disabled) return;

    const action = button.dataset.action;

    if (!["star", "delete"].includes(action)) return;

    if (action === "delete" && !window.confirm("Hapus proyek ini?")) {
        return;
    }

    button.disabled = true;

    try {
        const pattern = action === "star"
            ? projectsPage.dataset.starUrl
            : projectsPage.dataset.deleteUrl;

        await writeProject(
            projectEndpoint(pattern, button.dataset.id),
            action === "star" ? "POST" : "DELETE"
        );

        showToast(
            "Berhasil",
            action === "star"
                ? "Status star diperbarui."
                : "Proyek berhasil dihapus.",
            "success"
        );

        await fetchProjects(searchInput.value.trim());
    } catch (error) {
        showToast("Permintaan gagal", error.message, "error", 6000);
    } finally {
        button.disabled = false;
    }
});

fetchProjects(searchInput.value.trim());
