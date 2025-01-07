$(document).ready(function() {
    // Initialize Select2 for "Favorite Notes"
    $('#notes').select2({
        tags: true,
        tokenSeparators: [',', ' '],
        placeholder: "Enter or select notes",
        ajax: {
            url: '/select2-data',
            dataType: 'json',
            processResults: function (data) {
                console.log("Notes data received:", data.notes); // Debugging line
                return {
                    results: data.notes
                };
            }
        },
        createTag: function (params) {
            var term = $.trim(params.term);
            if (term === '') {
                return null;
            }
            return {
                id: term,
                text: term,
                newTag: true // add additional parameters
            };
        },
        matcher: function(params, data) {
            console.log("Search term:", params.term);
            console.log("Data item:", data);
        
            if ($.trim(params.term) === '') {
                console.log("No search term, returning data:", data);
                return data;
            }
        
            if (typeof data.text === 'undefined') {
                console.log("No text property, skipping:", data);
                return null;
            }
        
            if (data.text.toLowerCase().startsWith(params.term.toLowerCase())) {
                console.log("Match found:", data);
                return $.extend({}, data, true);
            }
        
            console.log("No match:", data);
            return null;
        }
    });

    // Initialize Select2 for "Favorite Families"
    $('#families').select2({
        tags: true,
        tokenSeparators: [',', ' '],
        placeholder: "Enter or select families",
        ajax: {
            url: '/select2-data',
            dataType: 'json',
            processResults: function (data) {
                console.log("Families data received:", data.families); // Debugging line
                return {
                    results: data.families
                };
            }
        },
        createTag: function (params) {
            var term = $.trim(params.term);
            if (term === '') {
                return null;
            }
            return {
                id: term,
                text: term,
                newTag: true // add additional parameters
            };
        },
        matcher: function(params, data) {
            console.log("Search term:", params.term);
            console.log("Data item:", data);
        
            if ($.trim(params.term) === '') {
                console.log("No search term, returning data:", data);
                return data;
            }
        
            if (typeof data.text === 'undefined') {
                console.log("No text property, skipping:", data);
                return null;
            }
        
            if (data.text.toLowerCase().startsWith(params.term.toLowerCase())) {
                console.log("Match found:", data);
                return $.extend({}, data, true);
            }
        
            console.log("No match:", data);
            return null;
        }
    });

    const submitButton = document.getElementById("submitButton");
    const preferencesForm = document.getElementById("preferencesForm");
    const recommendationList = document.getElementById("recommendationList");

    submitButton.addEventListener("click", () => {
        const gender = document.getElementById("gender").value;
        const selectedNotes = $('#notes').select2('data').map(item => item.id);
        const selectedFamilies = $('#families').select2('data').map(item => item.id);

        console.log("Selected Notes:", selectedNotes);
        console.log("Selected Families:", selectedFamilies);

        const formData = {
            gender: gender,
            preferred_notes: selectedNotes,
            preferred_families: selectedFamilies
            // Add disliked_notes if needed
        };

        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
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
                
                    // Format the fragrance name
                    const formattedName = formatText(fragrance['Fragrance Name']);
                
                    // Format the brand name
                    const formattedBrand = formatText(fragrance['Brand']);
                
                    const name = document.createElement("h3");
                    name.textContent = formattedName; // Use the formatted fragrance name
                    const brand = document.createElement("p");
                    brand.textContent = `by ${formattedBrand}`; // Use the formatted brand name
                
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
});




// function formatText(text) {
//     return text.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
// }
function formatText(text) {
    return text
        .split('-') // Split the text by "-"
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize each word
        .join(' '); // Join the words back with a space
}
