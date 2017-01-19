/* globals group_id */
$(document).ready(function() {
    "use strict";

    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            // get_users defined in htm template
            "url": Flask.url_for('user.get_users'),
            "type": "get"
        }
    }, utils.datatables.defaults));

    // Enable the toggle on rows
    utils.datatables.enable_select(table);

    // group_id is defined in the template.
    utils.datatables.action_by_url(
        $('#add_users'), table,
        Flask.url_for('group.group_api_add_users', {group_id: group_id}),
        "put",
        Flask.url_for('group.view_users', {group_id: group_id})
    );
});
