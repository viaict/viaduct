$(document).ready(function() {
    "use strict";

    var mailtype_select = $("#mailtype");
    var maillist_input = $("#maillist");

    function update_maillist_enabled() {
        maillist_input.prop('disabled', mailtype_select.val() === 'none');
    }

    mailtype_select.on('change', update_maillist_enabled);

    update_maillist_enabled();
});
