/* Flash a message. */
function flash(message, type) {
	var $container = $('#messages');
	var $message = $('<div></div>');

	$message.addClass('alert').addClass('alert-' + type);
	$message.text(message);
	$message.hide();

	$container.prepend($message);
	$message.slideDown('slow');

	scrollToTop();
}

/* Clear the message area. */
function clearflash() {
	$('#messages .alert').slideUp('slow', function() {
		$(this).remove();
	});
}

/* Move up to the flash container if any messages were flashed. */
$(function() {
	if ($('#messages > div.alert').length > 0) {
		scrollToTop();
	}
});

/* Scroll to the message box. */
function scrollToTop() {
	$('html, body').animate({
		scrollTop: $('body').offset().top
	}, 'fast');
}
