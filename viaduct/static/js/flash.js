/* Flash a message. */
function flash(message, type) {
	var $container = $('#messages');
	var $message = $('<div></div>');

	$message.addClass('alert').addClass('alert-' + type);
	$message.text(message);
	$message.hide();

	$container.prepend($message);
	$message.slideDown('slow');
}

/* Clear the message area. */
function clearflash() {
	$('#messages .alert').slideUp('slow', function() {
		$(this).remove();
	});
}