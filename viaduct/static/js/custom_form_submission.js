$(document).ready(function() {
	$("#custom_form").click(function() {
		var custom_form = $(this).closest('form');

		$.post(
			custom_form.attr('action'), 
			{
				'user': $('#custom_form_user').serialize(), 
				'data':$('#custom_form_data').serialize()
			},

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
