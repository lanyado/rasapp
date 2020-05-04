function login() {
	const box = $('.field-password')[0];
	const password = $('#password-input').val();

	if (password) {
		$.post('/login', {
			password,
		}, (response) => {
			if (response.auth) {
				// eslint-disable-next-line no-self-assign
				window.location.href = window.location.href; // response.redirect_url
			} else {
				box.style.animation = 'shake 0.5s ease';
				document.getElementById('modal').style.backgroundColor = 'red';
			}
		});
	}
	// get rid of the animation
	box.addEventListener('animationend', () => {
		box.style.animation = '';
	});
}

// let the user to login on enter key press
$('input').on('keyup', (e) => {
	if (e.keyCode === 13) login();
});

$('.fa-arrow-left').on('click', () => {
	login();
});
