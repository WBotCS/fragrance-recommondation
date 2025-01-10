$(document).ready(function() {
    // Fetch data for Select2 from the server
    fetch('/select2-data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Initialize Select2 for "Favorite Notes"
            $('#notes').select2({
                tags: true,
                tokenSeparators: [',', ' '],
                placeholder: "Enter or select notes",
                data: data.notes
            });

            // Initialize Select2 for "Favorite Families"
            $('#families').select2({
                tags: true,
                tokenSeparators: [',', ' '],
                placeholder: "Enter or select families",
                data: data.families
            });

            // Initialize Select2 for "Disliked Notes"
            $('#disliked_notes').select2({
                tags: true,
                tokenSeparators: [',', ' '],
                placeholder: "Enter or select disliked notes",
                data: data.notes // Use the same data as "Favorite Notes"
            });
        })
        .catch(error => {
            console.error("Error fetching Select2 data:", error);
            // Display an error message to the user
            alert("Error loading data for the form. Please check the console for details.");
        });

    const submitButton = document.getElementById("submitButton");
    const preferencesForm = document.getElementById("preferencesForm");
    const recommendationList = document.getElementById("recommendationList");

    submitButton.addEventListener("click", () => {
        const gender = document.getElementById("gender").value;
        const selectedNotes = $('#notes').select2('data').map(item => item.text);
        const selectedFamilies = $('#families').select2('data').map(item => item.text);
        const selectedDislikedNotes = $('#disliked_notes').select2('data').map(item => item.text);

        console.log("Selected Notes:", selectedNotes);
        console.log("Selected Families:", selectedFamilies);
        console.log("Selected Disliked Notes:", selectedDislikedNotes);

        const formData = {
            gender: gender,
            preferred_notes: selectedNotes,
            preferred_families: selectedFamilies,
            disliked_notes: selectedDislikedNotes
        };

        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            console.log("Response status:", response.status);
            return response.json();
        })
        .then(recommendations => {
            console.log("Recommendations from server:", recommendations);

            recommendationList.innerHTML = ''; // Clear previous recommendations

            if (recommendations.length === 0) {
                console.log("No recommendations found.");
                const listItem = document.createElement("li");
                listItem.textContent = "No fragrances found matching your preferences.";
                recommendationList.appendChild(listItem);
            } else {
                recommendations.forEach(fragrance => {
                    console.log("Processing fragrance:", fragrance);
                    const panel = document.createElement("div");
                    panel.className = "recommendation-panel";
                    const formattedName = formatText(fragrance['Fragrance Name']);
                    const formattedBrand = formatText(fragrance['Brand']);
                    const name = document.createElement("h3");
                    name.textContent = formattedName;
                    const brand = document.createElement("p");
                    brand.textContent = `by ${formattedBrand}`;
                    panel.appendChild(name);
                    panel.appendChild(brand);
                    recommendationList.appendChild(panel);
                });
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });

    function formatText(text) {
        return text
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }
    // Floating Action Button and Pop-up Modal
    const fab = document.getElementById('fab');
    const popup = document.getElementById('popup');
    const close = document.getElementsByClassName('close')[0];

    fab.onclick = function() {
        popup.style.display = 'block';
    }

    close.onclick = function() {
        popup.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == popup) {
            popup.style.display = 'none';
        }
    }
});

function toggleFeedbackForm() {
    const form = document.getElementById("feedback-form");
    form.style.display = form.style.display === "none" || form.style.display === "" ? "block" : "none";
}

function submitFeedback() {
    // Get selected satisfaction level
    const satisfaction = document.querySelector('input[name="satisfaction"]:checked');
    const comment = document.getElementById("feedback-comment").value;

    if (satisfaction) {
        alert(`Thank you for your feedback!\nSatisfaction Level: ${satisfaction.value}\nComment: ${comment}`);
    } else {
        alert("Please select your satisfaction level.");
    }

    // Hide the form after submission
    document.getElementById("feedback-form").style.display = "none";
}
