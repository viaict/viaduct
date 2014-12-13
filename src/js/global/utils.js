"use strict";

utils = {};


$(document).ready(function() {

    utils.datatables = {};
    utils.datatables.defaults = {
        "processing":true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "language": {
            "paginate": {
                "next": "Volgende",
                "previous": "Vorige"
            }
        },
        "columnDefs": [ {
            "targets": [0],
            "visible": false,
            "searchable": false
        }]

    };

    utils.datatables.enable_select = function ($selector) {
        $selector.on( 'click', 'tr', function () {
            $(this).toggleClass('info');
        } );
    }

    utils.datatables.delete_by_url = function($selector, table, url) {
        $selector.click( function () {
            var selected_ids = [];
            var selected_users = "";
            var selected_rows = table.rows('.info')
            for (i = 0; i < selected_rows.data().length; i++) {
                selected_ids.push(selected_rows.data()[i][0]);
                selected_users += "- " + selected_rows.data()[i][1] + "\n";
            }
            var json_data = { "selected_ids" : selected_ids }
            if (confirm('Do you surely want to delete all these?\n' + selected_users )) {
                $.ajax({
                    type: "DELETE",
                    url: url,
                    contentType: 'application/json',
                    success: function (data) {
                        table.ajax.reload();
                    },
                    data: JSON.stringify(json_data, null, '\t')
                });

            } else {
                return;
            }
        } );

    }
} );
