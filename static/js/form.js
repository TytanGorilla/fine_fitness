// Function to show the form when the button is clicked
function showForm() {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "block";  // Shows the form

    // Hide the button container
    document.getElementById('buttonContainer').style.display = 'none';
}

// Function to dynamically add a new exercise row
function addExerciseRow() {
    const table = document.getElementById("exerciseTable").getElementsByTagName('tbody')[0];

    // Create a new row
    const newRow = table.insertRow();

    // Add the "exercise-row" class to the new row
    newRow.classList.add("exercise-row");

    // Insert cells and inputs for the new row
    newRow.innerHTML = `
        <td><input type="text" name="exercise_name[]" placeholder="Exercise" class="form-control"></td>
        <td><input type="number" name="load[]" placeholder="Load (kg)" class="form-control"></td>
        <td><input type="number" name="sets[]" placeholder="Sets" oninput="updateRepsFields(this)" class="form-control"></td>
        <td class="reps-cell">
            <!-- Reps input fields will be inserted here dynamically -->
        </td>
        <td><input type="number" name="rir[]" placeholder="RIR" class="form-control"></td>
    `;
}

// Optional: Ensure the form is hidden by default when the page loads
window.onload = function () {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "none";  // Hide the form initially
}

// Function to dynamically create reps fields based on the number of sets
function updateRepsFields(setsInput) {
    const sets = setsInput.value;
    const repsCell = setsInput.closest('tr').querySelector('.reps-cell');
    repsCell.innerHTML = ''; // Clear existing reps inputs

    for (let i = 0; i < sets; i++) {
        const repsInput = document.createElement('input');
        repsInput.type = 'number';
        repsInput.name = `reps[${setsInput.closest('tr').rowIndex}][${i}]`; // Use array-like notation
        repsInput.placeholder = `Reps Set ${i + 1}`;
        repsInput.classList.add('reps-input'); // Add styling class if needed
        repsInput.classList.add('form-control')
        repsCell.appendChild(repsInput);
    }
}

// JavaScript to manage active state
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function () {
        // Remove 'active' class from all links
        document.querySelectorAll('.nav-link').forEach(nav => nav.classList.remove('active'));

        // Add 'active' class to the clicked link
        this.classList.add('active');
    });
});
