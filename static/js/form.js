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
        <td><input type="text" name="exercise_name[]" placeholder="Exercise" class="form-control" required></td>
        <td><input type="number" name="load[]" placeholder="Load (kg)" class="form-control" required></td>
        <td><input type="number" name="sets[]" placeholder="Sets" oninput="updateRepsFields(this)" class="form-control" required></td>
        <td class="reps-cell"></td>
        <td><input type="number" name="rir[]" placeholder="RIR" class="form-control" required></td>
        <td><button type="button" class="btn btn-danger" onclick="confirmRemoveRow(this)">Remove</button></td>
    `;

    tableBody.appendChild(newRow);  // Append the new row
}

function confirmRemoveRow(button) {
    const row = button.closest('tr');
    const confirmDelete = confirm("Are you sure you want to delete this exercise?");
    if (confirmDelete) {
        row.remove();  // Remove the row if the user confirms
    }
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
        repsInput.placeholder = `Set ${i + 1} Reps`;
        repsInput.classList.add('reps-input', 'form-control');
        repsInput.required = true;  // Add the required attribute

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

// Flag to track if there are unsaved changes
let hasUnsavedChanges = false;

// Function to mark that there are unsaved changes
function markUnsavedChanges() {
    hasUnsavedChanges = true;
}

// Attach the input event to all form inputs to track changes
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', markUnsavedChanges);
});

// Listen for the beforeunload event
window.addEventListener('beforeunload', function (event) {
    if (hasUnsavedChanges) {
        const confirmationMessage = "You have unsaved changes. Are you sure you want to leave?";
        event.returnValue = confirmationMessage; // This line is required for most browsers
        return confirmationMessage; // For some browsers
    }
});

function fetchTrainingDays() {
    const programId = document.getElementById('program').value;
    const sessionDaySelect = document.getElementById('session_day');

    // Clear existing options
    sessionDaySelect.innerHTML = '<option value="" disabled selected>Select Day</option>';

    if (programId) {
        fetch(`/get_training_days/${programId}`)
            .then(response => response.json())
            .then(data => {
                data.forEach(([day, day_name]) => {
                    const option = document.createElement('option');
                    option.value = day;
                    option.textContent = day_name;
                    sessionDaySelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching training days:', error);
            });
    }
}

function fetchTrainingWeeks() {
    const programId = document.getElementById('program').value;
    const weekDropdown = document.getElementById('week_number');

    // Clear existing options
    weekDropdown.innerHTML = '<option value="" disabled selected>Select a Week</option>';

    if (programId) {
        fetch(`/get_training_weeks/${programId}`)
            .then(response => response.json())
            .then(data => {
                const totalWeeks = data.total_weeks;
                if (totalWeeks > 0) {
                    // Populate the dropdown with week numbers from 1 to maxWeek
                    for (let i = 1; i <= totalWeeks; i++) {
                        const option = document.createElement('option');
                        option.value = i;
                        option.textContent = `Week ${i}`;
                        weekDropdown.appendChild(option);
                    }
                } else {
                    console.log('No training weeks found for this program.');
                }
            })
            .catch(error => {
                console.error('Error fetching training weeks:', error);
            });
    }
}


