$(function() {
    'use strict';

    // Initialize the nominee selector with all pre-nominated names.
    var nominees = [];
    _(viaduct.nominees).forEach(function(nominee) {
        nominees.push({id: nominee.id, text: nominee.name});
    });
    $('#nominee_select').select2({tags: nominees, maximumSelectionSize: 1});

    // Submit nomination.
    $('.container form').submit(function(e) {
        e.preventDefault();

        var $this = $(this);

        var $btn = $this.find('button');
        $btn.prop('disabled', true);

        var selection = $this.find('#nominee_select').select2('data')[0];

        if (selection === undefined) {
            $btn.prop('disabled', false);
            return;
        }

        var nominee_id;
        if (selection.id !== selection.text) {
            nominee_id = selection.id;
        }

        var data = {name: selection.text, id: nominee_id};

        $.post(viaduct.nominate_url, data, function() {
            location.reload();
        }).fail(function(jqHXR) {
            var error = $.parseJSON(jqHXR.responseText).error;

            clearflash();
            flash(error, 'error');

            $btn.prop('disabled', false);
        });
    });
});
