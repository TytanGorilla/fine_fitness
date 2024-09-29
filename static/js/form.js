// Function to show the form when the button is clicked
function showForm() {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "block";  // Shows the form

    // Hide the button container
    document.getElementById('buttonContainer').style.display = 'none';
}


// Optional: Ensure the form is hidden by default when the page loads
window.onload = function () {
    const exerciseForm = document.getElementById("exerciseForm");
    exerciseForm.style.display = "none";  // Hide the form initially
}

// Function to dynamically add a new exercise row
function addExerciseRow() {
    const tableBody = document.querySelector("#exerciseTable tbody");
    const newRow = document.createElement('tr');
    newRow.classList.add("exercise-row");

    newRow.innerHTML = `
        <td><input type="text" name="exercise_name[]" placeholder="Exercise" class="form-control"></td>
        <td><input type="number" name="load[]" placeholder="Load (kg)" class="form-control"></td>
        <td><input type="number" name="sets[]" placeholder="Sets" oninput="updateRepsFields(this)" class="form-control"></td>
        <td class="reps-cell"></td>
        <td><input type="number" name="rir[]" placeholder="RIR" class="form-control"></td>
    `;

    tableBody.appendChild(newRow);  // Append the new row
}


// Function to dynamically create reps fields based on the number of sets
function updateRepsFields(setsInput) {
    const row = setsInput.closest('tr');  // Get the closest table row
    const rowIndex = Array.from(row.parentNode.children).indexOf(row);  // Get the index of the row
    const setsValue = parseInt(setsInput.value) || 0;  // Get the number of sets
    const repsCell = row.querySelector('.reps-cell');  // Find the reps cell in the current row

    // Clear any existing reps input fields
    repsCell.innerHTML = '';

    // Add reps input fields based on the number of sets
    for (let i = 0; i < setsValue; i++) {
        const repsInput = document.createElement('input');
        repsInput.type = 'number';
        repsInput.name = `reps[${rowIndex}][]`;  // Use the row index for the exercise  // Use the row index and set index
        repsInput.placeholder = `Reps Set ${i + 1}`;
        repsInput.classList.add('reps-input', 'form-control');

        repsCell.appendChild(repsInput);  // Append the new input field
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
