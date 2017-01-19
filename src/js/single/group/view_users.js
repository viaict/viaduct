/* global group_id */
$(document).ready(function() {
    "use strict";

    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            // get_group_users variable defined in template
            "url": Flask.url_for('group.get_group_users', {group_id: group_id}),
            "type": "get"
        }
    }, utils.datatables.defaults));

    utils.datatables.enable_select($('#datatable tbody'));

    // delete_group_users variable defined in template
    utils.datatables.action_by_url(
        $('#delete'), table,
        Flask.url_for('group.delete_group_users', {group_id: group_id}),
        "delete"
    );
});
