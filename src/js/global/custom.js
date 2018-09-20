$(document).ready(function() {
    'use strict';

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
