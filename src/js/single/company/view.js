function format(d) {
    return '<a href="'+ d.view +'">'+
        '<img class="img-rounded" style="max-width:250px; max-height:100px;" '+
        'src="/static/files/'+ d.logo +'"></img></a>' +
        '<p><i class="glyphicon glyphicon-envelope"></i><a target="blank_" ' +
        'href="mailto:'+ d.contact.email +'">'+ d.contact.email +'</a>';
}

$(document).ready(function() {
    var table = $('#datatable').DataTable(_.defaults({
        "ajax": {
            "url": get_companies,
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
                "className": "details-control",
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
            row.child(format(row.data())).show();
            tr.addClass('shown');
        }
    });
});
