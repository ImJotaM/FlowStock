document.getElementById('edit-name-btn').addEventListener('click', function() {
	document.getElementById('name-view').classList.add('d-none');
	document.getElementById('name-edit-form').classList.remove('d-none');
});

document.getElementById('cancel-name-edit').addEventListener('click', function() {
	document.getElementById('name-edit-form').classList.add('d-none');
	document.getElementById('name-view').classList.remove('d-none');
});

document.getElementById('edit-email-btn').addEventListener('click', function() {
	document.getElementById('email-view').classList.add('d-none');
	document.getElementById('email-edit-form').classList.remove('d-none');
});

document.getElementById('cancel-email-edit').addEventListener('click', function() {
	document.getElementById('email-edit-form').classList.add('d-none');
	document.getElementById('email-view').classList.remove('d-none');
});

document.getElementById('edit-password-btn').addEventListener('click', function() {
	document.getElementById('password-view').classList.add('d-none');
	document.getElementById('password-edit-form').classList.remove('d-none');
});

document.getElementById('cancel-password-edit').addEventListener('click', function() {
	document.getElementById('password-edit-form').classList.add('d-none');
	document.getElementById('password-view').classList.remove('d-none');
});