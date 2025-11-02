document.addEventListener('DOMContentLoaded', function() {
    // --- Initialize Number Formatter ---
    // Use the modern Intl.NumberFormat for correct Indo-Arabic numerals.
    const indoArabicFormatter = new Intl.NumberFormat('ar-IQ');

    // --- Element Selectors ---
    const displays = {
        stems: document.getElementById('stems-count-display'),
        derived: document.getElementById('derived-count-display'),
        verbs: document.getElementById('verbs-count-display'),
        particles: document.getElementById('particles-count-display'),
        total: document.getElementById('total-count-display')
    };

    /**
     * Animates a number from 0 to a target value, updating the element's text.
     * @param {HTMLElement} element - The HTML element to update.
     * @param {number} target - The final number to count up to.
     * @param {number} [duration=2000] - The animation duration in milliseconds.
     */
    function animateCount(element, target, duration = 2000) {
        if (!element || isNaN(target)) return;
        let start = 0;
        const stepTime = 20; // Update every 20ms
        const totalSteps = duration / stepTime;
        const increment = target / totalSteps;

        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                start = target;
                clearInterval(timer);
            }
            // Format the number at each step of the animation.
            element.textContent = indoArabicFormatter.format(Math.floor(start));
        }, stepTime);
    }

    // --- Fetch and Display Stats ---
    fetch('/api/get_word_counts')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            for (const key in displays) {
                if (data.hasOwnProperty(key)) {
                    animateCount(displays[key], data[key]);
                }
            }
        })
        .catch(error => {
            console.error("Could not fetch word count:", error);
            // Provide a user-friendly error message
            Object.values(displays).forEach(el => { if (el) el.textContent = "ھەڵە"; });
        });
});