$(document).ready(function() {
	$("#custom_form").click(function() {
		var custom_form = $(this).closest('form');

		$.post(
			custom_form.attr('action'), 
			{
				'phone_nr': custom_form.find('input[name="phone_nr"]').val(), 
				'data': $('#custom_form_data').find(':input').serialize()
			},

			function(result) {
				if (result == "success")
					flash("Je hebt het formulier succesvol ingevuld", "success");
				else if (result == "edit")
					flash("Je formulier is aangepast", "alert");
				else
					flash("Er is iets misgegaan bij het invullen :(", "error"); 
			}
		);

		return false;
	});
});
