(function($) {
$.fn.unserializeForm = function(values) {
	var form   = $(this);
	var values = decodeURIComponent(values.replace(/\+/g, ' ')).split("&");

	$.each(values, function() {
		var properties = this.split("=");
		var field = form.find(':input[name="' + properties[0] + '"]').first();

		if (field.attr('type') === 'checkbox')
			form.find(':checkbox[value="'+ properties[1] +'"]').prop('checked', true);
		else if (field.is('input') || field.is('textarea'))
			field.val(properties[1]);
		else if (field.is('select'))
			field.find(':option[value="'+ properties[1] +'"]').prop('selected', true);
	});
}
})(jQuery);
