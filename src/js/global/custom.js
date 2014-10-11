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

            // var $read_more_link = $('<a>Meer lezen</a>');
            // $read_more_link.attr('href', '#');
            // $read_more_link.on('click', function() {
            //     console.log('test');
            //     $main_block.toggleClass("mainpage_scroll");
            //     // if (Math.floor($main_block.height()) == desired_height) {
            //     //     $main_block.animate({'height': sprintf('%dpx',
            //     //                         actual_height + 20),
            //     //                         'overflow': 'visible'});
            //     //     $(this).text('Minder lezen');
            //     // }
            //     // else {
            //     //     $main_block.animate({'overflow': 'hidden',
            //     //                     'height': sprintf('%dpx', desired_height)});
            //     //     $(this).text('Meer lezen');
            //     // }

            //     return false;
            // });

            $read_more_div.append($read_more_link);

            $(this).prepend($read_more_div);
        }
    });

    /* PimPy functions */

    /* updates the task status */
    $('.pimpy_status').click(function() {
        var task_id = $(this).data('task-id');
        var status = $(this).data('status-id');
        $.getJSON('/pimpy/tasks/update_status', {
            task_id: task_id,
            new_status: status
        }, function(data) {
            $('#pimpy_task'+task_id).attr('class', 'btn dropdown-toggle ' + data.status);
            $('#pimpy_task_row_'+task_id).attr('class', 'pimpy_status_' + data.status);
        });
    });

    /* Editable Setting */
    $.fn.editable.defaults.mode = 'inline';
    /* Makes tasks content editable */
    $('.pimpy_editable').editable();
    $('.pimpy_editable_toggle').click(function() {
        $('.pimpy_editable').editable('toggleDisabled');
    });
    $('.pimpy_editable_date').editable({
        format: 'yyyy-mm-dd',
        viewformat: 'dd/mm/yyyy',
        datepicker: {
            weekStart: 1
        }
    });
    $('.pimpy_editable').editable('toggleDisabled');

    $(".btn-filter").on("click",function(){
      var classes = this.attributes['data-hide'].value;
      console.log()
      if ($(this).hasClass('active')) {
        $("tr.pimpy_status_"+classes).hide()
      } else {
        $("tr.pimpy_status_"+classes).show()
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


});
