$(document).ready(function() {
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            // get_users defined in htm template
            "url":get_users,
            "type": "get"
        }
    }, utils.datatables.defaults));

    // Enable the toggle on rows
    utils.datatables.enable_select(table);

    // group_api_add_users and group_view_users defined in htm template.
    utils.datatables.action_by_url($('#add_users'), table,
        group_api_add_users, "put", group_view_users);
});
