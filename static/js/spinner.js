document.addEventListener('DOMContentLoaded', function () {
    // Shows the loading spinner
    function showLoadingSpinner() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = 'flex';
        }
    }

    // Hides the loading spinner
    function hideLoadingSpinner() {
        const spinner = document.getElementById('loadingSpinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    }

    // Attaches event listeners to all forms on the page to show the spinner on submit
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            showLoadingSpinner();
        });
    });
});
