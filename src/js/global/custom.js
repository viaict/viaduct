$(document).ready(function() {
    /* Expander for the home page.
     * Creates a 'read more' button
     */
    $('.custom_expander').each(function() {
        var desired_height_text = $(this).css('min-height');
        var desired_height = parseInt(desired_height_text.
                                    substr(0, desired_height_text.length - 2));

        var actual_height = Math.floor($(this).height());

        if (actual_height > desired_height) {
            $main_block = $(this);

            $(this).css({'overflow': 'hidden', 'overflow-y': 'scroll',
                        'height': sprintf('%dpx', desired_height),
                        'position': 'relative'});

            var $read_more_div = $('<div></div>');
            $read_more_div.css({'height': $(this).css('margin-bottom'),
                                'left': sprintf('-%s',
                                                $(this).css('margin-left')),
                                'padding': $(this).css('margin'),
                                'padding-left': $(this).css('padding-left'),
                                'width': $(this).css('width')});
            $read_more_div.addClass('readmore');

            $read_more_div.append($read_more_link);

            $(this).prepend($read_more_div);
        }
    });

    /* sponsor carousel */
    $(function() {

        var $c = $('#carousel'),
            $w = $(".container");

        $c.carouFredSel({
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

    $(document).on('click', '.hide_nav_entry', function(e){
        console.log("test");
        $(this).hide();
        $(this).siblings(".show_nav_entry").show();
        $(this).parent().children().find(".nav_entry").fadeOut( "normal", function() {
            // Animation complete.
        });
    });

    $(document).on('click', '.show_nav_entry', function(e){
        $(this).hide();
        $(this).siblings(".hide_nav_entry").show();
        $(this).parent().children().find(".nav_entry").fadeIn( "normal", function() {
            // Animation complete.
        });
    });

    $('.confirm', '.confirmation').on('click', function() {
        return confirm("Are you sure you want to do this?");
    });
});
