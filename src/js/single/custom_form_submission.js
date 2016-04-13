$(document).ready(function() {
    /*!
     * jQuery serializeObject - v0.2 - 1/20/2010
     * http://benalman.com/projects/jquery-misc-plugins/
     *
     * Copyright (c) 2010 "Cowboy" Ben Alman
     * Dual licensed under the MIT and GPL licenses.
     * http://benalman.com/about/license/
     */

    'use strict';
    (function($, undefined) {
      $.fn.serializeObject = function(){
        var obj = {};

        $.each(this.serializeArray(), function(i,o){
          var n = o.name,
            v = o.value;

            obj[n] = obj[n] === undefined ? v
              : $.isArray( obj[n] ) ? obj[n].concat( v )
              : [ obj[n], v ];
        });

        return obj;
      };

    })(jQuery);

    var msg_success = "Je hebt het formulier succesvol ingevuld";


    $("form#custom").submit(function() {
        var custom_form = $(this);
        var validated   = true;

        // Validate required input fields
        custom_form.find('.control-group').each(function() {
            if ($(this).attr('req') == 'true')
                if ($(this).find('input').val() === '') {
                    validated = false;
                    $(this).find('input').css('border-color', 'red');
                }
        });

        if (validated) {
            var args = $.extend(
                custom_form.serializeObject(),
                {'data': $('#custom_form_data').find(':input').serialize()}
            );

            $.post(
                custom_form.attr('action'), args,

                function(result) {
                    if (result == "success")
                        flash(msg_success, "success");
                    else if (result == "edit")
                        flash("Je formulier is aangepast", "warning");
                    else if (result == 'reserve')
                        flash('Je staat op de reserve lijst', 'success');
                    else
                        flash("Er is iets misgegaan bij het invullen :(", "danger");
                }
            ).always(function() {
                utils.form.submit_button(custom_form).button('reset');
            });
        }

        return false;
    });
});
