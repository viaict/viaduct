$(document).ready(function() {
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": get_users,
            "type": "get"
        }
    }, utils.datatables.defaults));

    /* Enable user profile selection */
    $('#datatable').on('click', 'tr', function () {
        window.open("/users/view/" + table.row(this).data()[0]);
    });

    utils.datatables.action_by_url( $('#delete'), table, delete_users, "delete"
    );
});
