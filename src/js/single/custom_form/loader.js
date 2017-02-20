$(function () {
    'use strict';

    $('.custom-form-field').each(function () {
        var $this = $(this);

        var $slct = $('select', $this);
        var $btn_reload = $('.form-reload', $this);
        var $spn_refresh = $('.refresh', $btn_reload);
        var $spn_loading = $('.loading', $btn_reload);

        $spn_refresh.hide();

        $slct.data('data-value', $slct.val());
        get_entries($slct, $btn_reload, $spn_refresh, $spn_loading);

        $btn_reload.click(function () {
            $slct.data('value', $slct.val());
            get_entries($slct, $btn_reload, $spn_refresh, $spn_loading);
        });
    });

    function get_entries($slct, $btn, $refr, $load) {
        $btn.prop('disabled', true);
        $refr.hide();
        $load.show();

        var current = parseInt($slct.data('value'));

        $slct.children(':not(.empty)').remove();

        $.getJSON(Flask.url_for('custom_form.loader', {'current': current}),
                function (data) {
            var forms = data.forms;

            for (var group_i in forms) {
                var group = forms[group_i];

                if (group[1].length === 0) {
                    continue;
                }

                var $optgroup = $('<optgroup></optgroup>').appendTo($slct);
                $optgroup.attr('label', group[0]);

                for (var opt_i in group[1]) {
                    var opt = group[1][opt_i];

                    var $option = $('<option></option>').appendTo($optgroup);
                    $option.text(opt.name);
                    $option.val(opt.id);

                    if (current === opt.id) {
                        $option.prop('selected', true);
                    }
                }
            }

            finish();
        }).error(function () {
            finish();
        });

        function finish() {
            $load.hide();
            $refr.show();
            if($slct.hasClass("select2-offscreen"))
                $slct.select2();
            $btn.prop('disabled', false);
        }
    }
});
