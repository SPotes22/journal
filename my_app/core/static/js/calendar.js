document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".task-form").forEach((details) => {
        details.addEventListener("toggle", () => {
            if (details.open) {
                const input = details.querySelector('input[name="title"]');
                if (input) input.focus();
            }
        });
    });
});
