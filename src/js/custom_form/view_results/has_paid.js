$(document).ready(function() {
    $(".has_paid").click(function() {
        $.post("/forms/has_paid/" + this.id);

        // Adjust the money icon -> change it to "Ok" icon
        $(this).find('i')
            .toggleClass('glyphicon-unchecked glyphicon-check');
    });
});
