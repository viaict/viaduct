$(document).ready(function() {
    "use strict";

    $(".confirmation").click(function(ev) {
        if (!confirm("Weet je ZEKER dat je dit wilt doen?!")) {
            ev.preventDefault();
        }
    });
});
