document.addEventListener('DOMContentLoaded', function() {
    // Edit button click handler
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent the row click event
            const stockId = this.getAttribute('data-stock-id');
            
            // Hide the name and show the edit form
            document.getElementById(`stock-name-${stockId}`).classList.add('d-none');
            document.getElementById(`stock-edit-form-${stockId}`).classList.remove('d-none');
            
            // Focus on the input field
            document.querySelector(`#stock-edit-form-${stockId} input[name="new_name"]`).focus();
        });
    });

    // Cancel button click handler
    document.querySelectorAll('.cancel-edit').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent the row click event
            const stockId = this.getAttribute('data-stock-id');
            
            // Hide the edit form and show the name
            document.getElementById(`stock-edit-form-${stockId}`).classList.add('d-none');
            document.getElementById(`stock-name-${stockId}`).classList.remove('d-none');
        });
    });

    // Prevent form submission from triggering row click
    document.querySelectorAll('.stock-edit-form').forEach(form => {
        form.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });

    // Prevent input field from triggering row click
    document.querySelectorAll('.stock-edit-form input').forEach(input => {
        input.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});