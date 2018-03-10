$(document).ready(function() {
    "use strict";

    var custom_read_bool = $("#custom_read_permission");
    var custom_read_select = $("#read_groups");

    function update_select_read_groups() {
        custom_read_select.prop('disabled', custom_read_bool.is(":checked") === false);
    }

    custom_read_bool.on('change', update_select_read_groups);

    update_select_read_groups();
});
