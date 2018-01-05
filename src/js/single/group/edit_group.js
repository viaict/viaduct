$(document).ready(function() {
    "use strict";

    var mailtype_select = $("#mailtype");
    var maillist_input = $("#maillist");

    function update_maillist_enabled() {
        if(mailtype_select.val() === 'none') {
            maillist_input.prop('disabled', true);
        }
        else {
            maillist_input.prop('disabled', false);
        }
    }

    mailtype_select.on('change', update_maillist_enabled);

    update_maillist_enabled();
});
