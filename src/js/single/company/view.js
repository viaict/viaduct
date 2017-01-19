function format(d, table) {
    "use strict";

    d.table = table;
    return utils.jadetpl('company_list_datatable', d);
}

$(document).ready(function() {
    "use strict";

    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": Flask.url_for('company.get_companies'),
            "type": "get",
        },
        "columns": [
            { "data": "id" },
            {
                "className": "details-control",
                "data": "name"
            },
            {
                "className": "details-control",
                "data": "website"
            },
            {
                "className": "search",
                "data": "location.city"
            }
        ]
    }, utils.datatables.defaults));

    $("#datatable tbody").on('click', 'td.details-control', function() {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            row.child(format(row.data(), table)).show();
            tr.addClass('shown');
        }
    });
});
