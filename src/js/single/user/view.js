$(document).ready(function() {
    "use strict";

    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": Flask.url_for('user.get_users'),
            "type": "get"
        }
    }, utils.datatables.defaults));

    /* Enable user profile selection */
    $('#datatable').on('click', 'tr', function () {
        window.open(
            Flask.url_for('user.view_single', {
                user_id: table.row(this).data()[0]
            })
        );
    });

    utils.datatables.action_by_url(
        $('#delete'), table, Flask.url_for('user.api_delete_user'), "delete"
    );
});
