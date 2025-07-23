document.querySelectorAll('.edit-btn').forEach(button => {
	button.addEventListener('click', function(e) {
		e.preventDefault();
		e.stopPropagation();
		const stockId = this.getAttribute('data-stock-id');

		document.querySelectorAll('.stock-edit-form').forEach(form => {
			form.classList.add('d-none');
		});
		document.querySelectorAll('.stock-name').forEach(nameSpan => {
			nameSpan.classList.remove('d-none');
		});

		if (stockId) {
			const nameSpan = document.getElementById(`stock-name-${stockId}`);
			const form = document.getElementById(`stock-edit-form-${stockId}`);
			const input = form?.querySelector('input[name="name"]');

			if (nameSpan && form && input) {
				nameSpan.classList.add('d-none');
				form.classList.remove('d-none');

				input.focus();
				const val = input.value;
				input.value = '';
				input.value = val;
			}
		}
	});
});


document.querySelectorAll('.cancel-edit').forEach(button => {
	button.addEventListener('click', function(e) {

		e.preventDefault();
		e.stopPropagation();
		
		const stockId = this.getAttribute('data-stock-id');
		
		if (stockId) {

			const nameSpan = document.getElementById(`stock-name-${stockId}`);
			const form = document.getElementById(`stock-edit-form-${stockId}`);
			const input = form?.querySelector('input[name="name"]');

			if (nameSpan && form && input) {
				nameSpan.classList.remove('d-none');
				form.classList.add('d-none');
				input.focus();
			}

		}

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

window.addEventListener('DOMContentLoaded', () => {

	const urlParams = new URLSearchParams(window.location.search);
	const stockId = urlParams.get('edit_id');

	if (stockId) {

		document.querySelectorAll('.stock-edit-form').forEach(form => {
			form.classList.add('d-none');
		});
		document.querySelectorAll('.stock-name').forEach(nameSpan => {
			nameSpan.classList.remove('d-none');
		});

		const nameSpan = document.getElementById(`stock-name-${stockId}`);
		const form = document.getElementById(`stock-edit-form-${stockId}`);
		const input = form?.querySelector('input[name="name"]');

		if (nameSpan && form && input) {
			nameSpan.classList.add('d-none');
			form.classList.remove('d-none');

			input.focus();
			const val = input.value;
			input.value = '';
			input.value = val;
		}
	}
});