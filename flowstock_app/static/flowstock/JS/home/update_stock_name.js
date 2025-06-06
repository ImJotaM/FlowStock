document.querySelectorAll('.edit-btn').forEach(button => {
	button.addEventListener('click', function(e) {
		e.preventDefault();
		e.stopPropagation();
		const stockId = this.getAttribute('data-stock-id');
		
		document.getElementById(`stock-name-${stockId}`).classList.add('d-none');
		document.getElementById(`stock-edit-form-${stockId}`).classList.remove('d-none');
		
		document.querySelector(`#stock-edit-form-${stockId} input[name="new_name"]`).focus();
	});
});

document.querySelectorAll('.cancel-edit').forEach(button => {
	button.addEventListener('click', function(e) {
		e.preventDefault();
		e.stopPropagation();
		const stockId = this.getAttribute('data-stock-id');
		
		document.getElementById(`stock-edit-form-${stockId}`).classList.add('d-none');
		document.getElementById(`stock-name-${stockId}`).classList.remove('d-none');
	});
});

document.querySelectorAll('.stock-edit-form').forEach(form => {
	form.addEventListener('click', function(e) {
		e.stopPropagation();
	});
});

document.querySelectorAll('.stock-edit-form input').forEach(input => {
	input.addEventListener('click', function(e) {
		e.stopPropagation();
	});
});