var keeswildeleteknopje = $(".keeswildeleteknopje");

keeswildeleteknopje.click(function() {
	if (confirm("Hoi kees, weet je zeker dat je deze wilt verwijderen?")) {
		
		$.post("/forms/remove/" + this.id);
		$(this).closest("tr").fadeOut(300);
	}
});
