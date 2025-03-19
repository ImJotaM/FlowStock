const register_button = document.getElementById("button-go-register");
register_button.addEventListener("click", ChangeToRegister);

const login_form = document.getElementById('form-container-login');
const register_form = document.getElementById('form-container-register');

function ChangeToRegister() {
    
    login_form.style.display = 'none';
    register_form.style.display = 'flex';

}