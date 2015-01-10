$(function () {
    'use strict';

    var $coordinator_select = $('#coordinator_id');
    var $group_select = $('#group_id');

    $coordinator_select.select2();
    $group_select.select2();

    function set_group_users() {
        var group_id = $group_select.val();

        $.get('/api/group/users/' + group_id, {}, function (data) {
            $coordinator_select.empty();

            _(data.users).forEach(function (user) {
                var $option = $('<option></option>');
                $option.val(user.val);
                $option.text(user.label);

                $coordinator_select.append($option);
            });
        });
    }

    $group_select.change(function () {
        set_group_users();
    });
});
