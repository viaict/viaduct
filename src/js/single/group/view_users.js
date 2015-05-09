$(document).ready(function() {
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            // get_group_users variable defined in template
            "url": get_group_users,
            "type": "get"
        }
    }, utils.datatables.defaults));

    utils.datatables.enable_select($('#datatable tbody'));

    // delete_group_users variable defined in template
    utils.datatables.action_by_url($('#delete'), table,
                                   delete_group_users, "delete");
});
