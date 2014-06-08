var $delete_form = $('form#delete');
var $delete_btn = $('button#btn-delete');

$delete_form.hide();

$delete_btn.click(function() {
    if (confirm('Weet u zeker dit nieuwsartikel te willen verwijderen?')) {
        $delete_form.submit();
    }
});
