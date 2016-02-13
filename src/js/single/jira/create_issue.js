$(function() {
    $('#report_form button[type=submit]').on('click', function (e) {
        $(this).button('loading');
    });
});
