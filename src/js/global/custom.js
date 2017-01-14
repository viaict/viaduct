$(document).ready(function() {
    'use strict';

    /* sponsor carousel */
    $(function() {

        var $c = $('#carousel');

        $c.carouFredSel({
            height: 180,
            align: false,
            items: 6,
            scroll: {
                items: 1,
                duration: 4000,
                timeoutDuration: 0,
                easing: 'linear',
                pauseOnHover: 'immediate'
            }
        });


        /*$w.bind('resize.example', function() {
            var nw = $w.width();

            $c.width(nw * 3);
            $c.parent().width(nw);

        }).trigger('resize.example');*/
    });

    /* This is done like this because these entries are added to the page
     * dynamically. Otherwise, we would have to assign this event every time
     * an entry is added to the page. */

    $(document).on('click', '.hide_nav_entry', function(){
        console.log("test");
        $(this).hide();
        $(this).siblings(".show_nav_entry").show();
        $(this).parent().children().find(".nav_entry").fadeOut( "normal", function() {
            // Animation complete.
        });
    });

    $(document).on('click', '.show_nav_entry', function(){
        $(this).hide();
        $(this).siblings(".hide_nav_entry").show();
        $(this).parent().children().find(".nav_entry").fadeIn( "normal", function() {
            // Animation complete.
        });
    });

    $('.confirm', '.confirmation').on('click', function() {
        return confirm("Are you sure you want to do this?");
    });

    $('.dotdotdot').dotdotdot({
        after: "a.readmore",
        watch: true,
    });


    /* Submit buttons should have a loading text once the form is submitted.
     * This is important so forms cannot be submitted multiple times.
     */

    $('form').on('submit', function() {
        var $button = utils.form.submit_button(this);
        utils.form.button_loading($button);
    });
});

Date.prototype.yyyymmdd = function() {
    "use strict";
    var mm = this.getMonth() + 1; // getMonth() is zero-based
    var dd = this.getDate();

    return [this.getFullYear(),
        (mm>9 ? '' : '0') + mm,
        (dd>9 ? '' : '0') + dd
    ].join('-');
};
