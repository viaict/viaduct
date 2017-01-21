$(function() {
    'use strict';

    var $btns = $('.container table a');
    $btns.click(function(e) {
        e.preventDefault();

        var $this = $(this);

        $btns.addClass('disabled');

        var nominee_id = $this.parents('tr').data('nominee-id');
        var valid = $this.hasClass('valid');

        var data = {id: nominee_id, valid: valid};

        $.post(viaduct.validate_url, data, function() {
            location.reload();
        }).fail(function(jqHXR) {
            var error = $.parseJSON(jqHXR.responseText).error;

            utils.flash.clear();
            utils.flash.new(error, 'danger');

            $btns.removeClass('disabled');
        });
    });
});
