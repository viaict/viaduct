var keeswildeleteknopje = $(".keeswildeleteknopje");

keeswildeleteknopje.click(function() {
	if (confirm($(this).attr("message"))) {
		
		$.post("/forms/remove/" + this.id);
		$(this).closest("tr").fadeOut(300);
	}
});
