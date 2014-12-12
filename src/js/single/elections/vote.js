$(function() {
    'use strict';

    // Submit vote.
    $('.container form').submit(function(e) {
        e.preventDefault();

        var $this = $(this);

        var $btn = $this.find('button');
        $btn.prop('disabled', true);

        var selection = $('input:checked', $this).val();

        if (selection === undefined) {
            $btn.prop('disabled', false);
            return;
        }

        var data = {nominee_id: selection};

        $.post(viaduct.vote_url, data, function() {
            location.reload();
        }).fail(function(jqHXR) {
            var error = $.parseJSON(jqHXR.responseText).error;

            clearflash();
            flash(error, 'error');

            $btn.prop('disabled', false);
        });
    });
});
