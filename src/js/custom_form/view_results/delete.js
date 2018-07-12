$(document).ready(function() {
    "use strict";

    $(".delete-form-result").click(function() {
        var self = $(this);

        if (confirm($(this).attr("message"))) {
            $.post(Flask.url_for("custom_form.remove_response", {
                form_id: self.data().formId,
                submission_id: self.data().submissionId
            }));
            $(this).closest("tr").fadeOut(300);
        }
    });
});
