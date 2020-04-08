
function login(){
    const box = $('.field-password')[0];
    const pass = $('#password-input').val();

    if (pass){
    	$.post('/login',{
        password: pass
    		},function(response){
            if (response.auth){
    				    window.location.href = response.redirect_url
            }
    			  else{
                box.style.animation = "shake 0.5s ease";
                document.getElementById("modal").style.backgroundColor = 'red';
           }
      	})
    }
    // GET RID OF ANIMATION
    box.addEventListener("animationend", () => {
        box.style.animation = "";
    })
}

// let the user to login on enter key press
$('input').keyup(function(e){
    if(e.keyCode == 13)
       login();
});

$('.fa-arrow-left').on("click", () => {
  login();
});
