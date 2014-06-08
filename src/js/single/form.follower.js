$(document).ready(function() {
    $("#follow_table .follow").click(function(e) {
        $(this).closest('tr').fadeOut();
    });

    $(".follow").click(function(e) {
        e.preventDefault();
        var t = $(this);
        t.toggleClass("btn-success btn-danger");

        $.post(this.href, function( data ) {
            t.html((data === "added" ? "Niet meer" : "Formulier") + " volgen");
        });
    });
});
