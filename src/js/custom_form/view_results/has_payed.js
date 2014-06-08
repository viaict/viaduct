$(".has_payed").click(function() {
	$.post("/forms/has_payed/" + this.id);

	// Adjust the money icon -> change it to "Ok" icon
	$(this).find('i')
		.toggleClass('glyphicon-unchecked glyphicon-check');
});
