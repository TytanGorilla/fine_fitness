// Function to show the form when the button is clicked
function showForm() {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "block";  // Shows the form
}

// Function to dynamically add a new exercise row
function addExerciseRow() {
    const table = document.getElementById("exerciseTable").getElementsByTagName('tbody')[0];

    // Create a new row
    const newRow = table.insertRow();

    // Insert cells and inputs for the new row
    newRow.innerHTML = `
        <tr>
            <td><input type="text" name="exercise_name[]" placeholder="Exercise"></td>
            <td><input type="number" name="load[]" placeholder="Load (kg)"></td>
            <td><input type="number" name="sets[]" placeholder="Sets" oninput="updateRepsFields(this)"></td>
            <td id="reps-cell">
                <!-- Reps input fields will be inserted here dynamically -->
            </td>
            <td><input type="number" name="rir[]" placeholder="RIR"></td>
        </tr>
    `;
}

// Optional: Ensure the form is hidden by default when the page loads
window.onload = function () {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "none";  // Hide the form initially
}

// Function to dynamically create reps fields based on the number of sets
function updateRepsFields(setsInput) {
    // Get the value of sets input (number of sets)
    const sets = parseInt(setsInput.value);

    // Get the cell where reps inputs will be placed
    const repsCell = setsInput.parentElement.nextElementSibling;

    // Clear any existing reps fields
    repsCell.innerHTML = '';

    // If the input is a valid number, create reps fields
    if (!isNaN(sets) && sets > 0) {
        for (let i = 1; i <= sets; i++) {
            const repsInput = document.createElement('input');
            repsInput.type = 'number';
            repsInput.name = 'reps[]';
            repsInput.placeholder = `Reps for Set ${i}`;
            repsInput.style.marginRight = '5px';
            repsCell.appendChild(repsInput);
        }
    }
}