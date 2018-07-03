$(document).ready(function() {
    "use strict";
    $(".has-paid").click(function() {
        var self = this;

        $.post("/forms/has_paid/" + this.id).done(function() {
            // Toggle check and color
            $(self).toggleClass('btn-danger btn-success');
            $(self).find('i').toggleClass('glyphicon-unchecked glyphicon-check');
        }).fail(function() {
            alert('Failed to update has paid field');
        })
    });
});
