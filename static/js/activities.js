// Enable horizontal scrolling with mouse wheel
document.querySelectorAll('.card-container').forEach(container => {
    container.addEventListener('wheel', function (event) {
        event.preventDefault();
        this.scrollLeft += event.deltaY;
    });
});

// Function to handle image loading error
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('img[data-placeholder]').forEach(img => {
        img.onerror = function() {
            this.src = this.getAttribute('data-placeholder');
        };
    });
});

// Local storage logic
document.addEventListener("DOMContentLoaded", function () {
    // Load saved state from localStorage when the page loads
    loadState();

    const checkboxes = document.querySelectorAll(".activity-checkbox");
    const collapses = document.querySelectorAll(".more-info");

    // Event listener for checkbox changes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", saveState);
    });

    // Event listener for collapsible sections (show/hide)
    collapses.forEach(collapse => {
        collapse.addEventListener("shown.bs.collapse", saveState);
        collapse.addEventListener("hidden.bs.collapse", saveState);
    });

    // Event listener for form submission to reset local storage
    document.querySelector("form").addEventListener("submit", function () {
        localStorage.removeItem("activityState");
    });
});

// Function to save the state (checkboxes and collapsible sections) to localStorage
function saveState() {
    const state = {};

    // Save checkbox state (checked or unchecked)
    document.querySelectorAll(".activity-checkbox").forEach(checkbox => {
        const checkboxId = checkbox.getAttribute("data-id");
        state[`checkbox-${checkboxId}`] = checkbox.checked;
    });

    // Save collapse state (expanded or collapsed)
    document.querySelectorAll(".more-info").forEach(collapse => {
        const collapseId = collapse.getAttribute("data-id");
        state[`collapse-${collapseId}`] = collapse.classList.contains("show");
    });

    // Save the state object to localStorage
    localStorage.setItem("activityState", JSON.stringify(state));
}

// Function to load the state from localStorage
function loadState() {
    const state = JSON.parse(localStorage.getItem("activityState"));
    if (!state) return;

    // Restore checkbox states
    document.querySelectorAll(".activity-checkbox").forEach(checkbox => {
        const checkboxId = checkbox.getAttribute("data-id");
        const checked = state[`checkbox-${checkboxId}`];
        if (checked !== undefined) {
            checkbox.checked = checked;
        }
    });

    // Restore collapse states
    document.querySelectorAll(".more-info").forEach(collapse => {
        const collapseId = collapse.getAttribute("data-id");
        const expanded = state[`collapse-${collapseId}`];
        if (expanded) {
            collapse.classList.add("show");
        }
    });
    
}
