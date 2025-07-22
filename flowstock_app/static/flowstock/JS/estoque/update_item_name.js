document.querySelectorAll('.item-edit-btn').forEach(button => {
	button.addEventListener('click', function (e) {
		e.preventDefault();
		e.stopPropagation();
		const itemId = this.getAttribute('data-item-id');

		document.getElementById(`item-display-${itemId}`).classList.add('d-none');
		document.getElementById(`item-edit-form-${itemId}`).classList.remove('d-none');

		document.querySelector(`#item-edit-form-${itemId} input[name="name"]`).focus();
	});
});

document.querySelectorAll('.cancel-edit').forEach(button => {
	button.addEventListener('click', function (e) {
		e.preventDefault();
		e.stopPropagation();
		const itemId = this.getAttribute('data-item-id');

		document.getElementById(`item-edit-form-${itemId}`).classList.add('d-none');
		document.getElementById(`item-display-${itemId}`).classList.remove('d-none');
	});
});

document.querySelectorAll('.item-edit-form').forEach(form => {
	form.addEventListener('click', function (e) {
		e.stopPropagation();
	});
});

document.querySelectorAll('.item-edit-form input').forEach(input => {
	input.addEventListener('click', function (e) {
		e.stopPropagation();
	});
});
