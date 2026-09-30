let toastTimer;
let toastHideTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toast = document.getElementById("toast-component");

    if (!toast) return;

    clearTimeout(toastTimer);
    clearTimeout(toastHideTimer);

    document.getElementById("toast-title").textContent = title;
    document.getElementById("toast-message").textContent = message;

    toast.dataset.type = type;

    if (!toast.matches(":popover-open")) {
        toast.showPopover();
        void toast.offsetHeight;
    }

    toast.classList.remove("toast-hidden");

    toastTimer = setTimeout(() => {
        toast.classList.add("toast-hidden");

        toastHideTimer = setTimeout(() => {
            toast.hidePopover();
        }, 250);
    }, duration);
}