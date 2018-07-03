$(document).ready(function() {
    var deleteFormResult = $(".delete-form-result");

    deleteFormResult.click(function() {
        if (confirm($(this).attr("message"))) {

            $.post("/forms/remove/" + this.id);
            $(this).closest("tr").fadeOut(300);
        }
    });
});
