/* globals get_language_for_extension*/

$(document).ready(function() {
    "use strict";
    $('select').select2();

    $('#file').on('change', function() {
        if(this.value === "")
            return;

        var fn = this.value.replace(/^.*[\\\/]/, '');
        var sp = fn.split('.');
        if(sp.length == 1)
            return;

        var extension = sp[sp.length - 1];

        var langid = get_language_for_extension(extension);
        if(langid !== null)
            $('#problem-language').select2('val', langid);
    });
});
