$(document).ready(function() {
    "use strict";
    $(".has-paid").click(function() {
        var self = $(this);

        $.post(Flask.url_for("custom_form.has_paid", {
                form_id: self.data().formId ,
                submission_id: self.data().submissionId
            })
        ).done(function() {
            // Toggle check and color
            self.toggleClass('btn-danger btn-success');
            self.find('i').toggleClass('glyphicon-unchecked glyphicon-check');
        }).fail(function() {
            alert('Failed to update has paid field');
        });
    });
});
