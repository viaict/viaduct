$(document).ready(function() {
    "use strict";
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": Flask.url_for('examination.get_educations'),
            "type": "get"
        }
    }, utils.datatables.defaults));

    $('#datatable').on('click', 'tr', function () {
        window.location.href = "/education/edit/" +
            table.row(this).data()[0] + "?redir=educations";
    });
});
