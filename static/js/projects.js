const projectsPage = document.getElementById("projects");
const searchForm = document.getElementById("project-search-form");
const searchInput = document.getElementById("search-input");
const grid = document.getElementById("grid");

const csrfInput = document.querySelector("#csrf-source input");
const csrfHtml = csrfInput.outerHTML;

const placeholderId = "00000000-0000-0000-0000-000000000000";

let projectsAbortController;
const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;

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

function buildProjectCardElement(item) {
    const project = item.fields;

    const article = document.createElement("article");
    article.className = "experience-card";

    const route = (template) => {
        return escapeHtml(
            template.replace(placeholderId, item.pk)
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
            <form
                method="post"
                action="${route(projectsPage.dataset.starUrl)}"
                class="star-form"
            >
                ${csrfHtml}

                <button
                    type="submit"
                    class="button button-star${project.is_starred ? " is-starred" : ""}"
                    aria-pressed="${project.is_starred ? "true" : "false"}"
                >
                    ★ ${project.is_starred ? "Unstar" : "Star"}

                    <span class="star-count">${count}</span>
                </button>
            </form>
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
            <form
                method="post"
                action="${route(projectsPage.dataset.deleteUrl)}"
                class="delete-project-form"
            >
                ${csrfHtml}

                <button
                    type="submit"
                    class="button button-danger"
                >
                    Hapus
                </button>
            </form>
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

    const deleteForm = article.querySelector(".delete-project-form");

    if (deleteForm) {
        deleteForm.addEventListener("submit", (event) => {
            if (!confirm("Hapus proyek ini?")) {
                event.preventDefault();
            }
        });
    }

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
            signal: controller.signal,
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const items = await response.json();

        if (controller.signal.aborted) return;

        grid.replaceChildren(
            ...items.map(buildProjectCardElement)
        );

        document.getElementById("empty").textContent = query
            ? "No matching projects found."
            : "No projects have been added yet.";

        displayPageSection(items.length ? "grid" : "empty");
    } catch (error) {
        if (error.name === "AbortError") return;

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

async function addProject(event) {
    event.preventDefault();

    const button = projectForm.querySelector(
        'button[type="submit"]'
    );

    if (button.disabled) return;

    button.disabled = true;

    try {
        const token = projectForm.querySelector(
            '[name="csrfmiddlewaretoken"]'
        ).value;

        const response = await fetch(
            projectForm.dataset.ajaxUrl,
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": token,
                    Accept: "application/json",
                },
                body: new FormData(projectForm),
                credentials: "same-origin",
            }
        );

        const result = await response
            .json()
            .catch(() => ({}));

        if (!response.ok) {
            const messages = result.errors
                ? Object.values(result.errors)
                    .flat()
                    .map((error) => error.message)
                : [
                    result.message ||
                    `Permintaan gagal (HTTP ${response.status}).`
                ];

            showToast(
                "Gagal menyimpan",
                messages.join(" "),
                "error",
                6000
            );

            return;
        }

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
            "Koneksi gagal",
            "Periksa koneksi, lalu coba lagi.",
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

fetchProjects(searchInput.value.trim());