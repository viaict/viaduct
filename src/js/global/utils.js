var utils = function() { // jshint ignore:line
    'use strict';
    var utils = {};
    utils.datatables =  {};

    var datatable_language;
    if (viaduct.locale == 'nl') {
        // If Dutch override english defaults. Translations taken from:
        // https://github.com/DataTables/Plugins/blob/master/i18n/Dutch.lang
        datatable_language = {
            "processing": "Bezig...",
            "lengthMenu": "_MENU_ resultaten weergeven",
            "zeroRecords": "Geen resultaten gevonden",
            "info": "_START_ tot _END_ van _TOTAL_ resultaten",
            "infoEmpty": "Geen resultaten om weer te geven",
            "infoFiltered": " (gefilterd uit _MAX_ resultaten)",
            "infoPostFix": "",
            "search": "Zoeken:",
            "emptyTable": "Geen resultaten aanwezig in de tabel",
            "infoThousands": ".",
            "loadingRecords": "Een moment geduld aub - bezig met laden...",
            "paginate": {
                "first": "Eerste",
                "last": "Laatste",
                "next": "Volgende",
                "previous": "Vorige"
            }
        };
    }

    utils.datatables.defaults = {
        "processing": true,
        "responsive": true,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "language": datatable_language,
        "columnDefs": [ {
            "targets": [0],
            "visible": false,
            "searchable": false
        }],
        "order": [
            [ 1, "asc"]
        ],
        "initComplete": function() {
            var api = this.api();
            api.$('td.search').click( function() {
                api.search( this.innerHTML ).draw();
            });
        }
    };

    utils.datatables.enable_select = function ($selector) {
        $selector.on( 'click', 'tr', function () {
            $(this).toggleClass('info');
        } );
    };

    utils.datatables.get_ids = function($selector, table) {
        var selected_ids = [];
        var selected_users = "";
        var selected_rows = table.rows('.info');
        for (var i = 0; i < selected_rows.data().length; i++) {
            selected_ids.push(selected_rows.data()[i][0]);
            selected_users += "- " + selected_rows.data()[i][1] + "\n";
        }
        return {"selected_ids": selected_ids};
    };

    utils.datatables.action_by_url = function(
        $selector, table, url, action, refer) {
        $selector.click(function () {
            var action_repr = "delete";
            if (action == "put") action_repr = "add";
            var json_data = utils.datatables.get_ids($selector, table);
            if (confirm('Are you sure you want to ' + action_repr + ' these?\n')) {
                $.ajax({
                    type: action,
                    url: url,
                    contentType: 'application/json',
                    success: function () {
                        if (action === "put") {
                            window.open(refer, "_top");
                        } else {
                            table.ajax.reload();
                        }
                    },
                    data: JSON.stringify(json_data, null, '\t'),
                });
            } else {
                return;
            }
        });
    };

    // this needs a tbody as helper element when it is generating table rows
    utils.jadetpl = function jadetpl(tpl, params, helper) {
        if (_.isUndefined(helper))
            helper = $('<div>');
        jade.render(helper[0], tpl, params);
        return helper.children();
    };


    utils.form = {};

    utils.form.submit_button = function($form) {
        // In a form a button without a type defaults to type submit
        return $('button[type!=button][type!=reset]', $form);
    };

    utils.form.button_loading = function($button) {
        if (viaduct.locale == 'en') {
            $button.button({loadingText: 'Loading...'});
        }
        else {
            $button.button({loadingText: 'Bezig...'});
        }

        $button.button('loading');
    };

    return utils;
}();
