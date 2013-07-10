$(document).ready(function() {
	$("#custom_form").click(function() {

		var custom_form = $(this).closest('form');
		var mail = $('input[name="mail"]').val();

		$.post(
			"/forms/submit/" + custom_form.attr('id'), 
			{'mail': mail, 'data':custom_form.serialize()},
			function(result) { 
				if (result == "success") {
					flash("Je hebt het formulier succesvol ingevuld", "success");
					custom_form.detach();
				}
				else if (result == "edit") {
					flash("Je formulier is aangepast", "alert");
					custom_form.detach();
				}
				else
					flash("Er is iets misgegaan bij het invullen :(", "error"); 
			}
		);

		return false;
	});
});
