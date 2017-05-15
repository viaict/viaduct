$(function () {
    'use strict';

    var btn_stati = 'btn-info btn-warning btn-success btn-danger';

    /* updates the task status */

    $('.pimpy_status').click(function () {
        var $this = $(this);

        var task_id = $this.data('task-id');
        var status = $this.data('status-id');

        var $task_rows = $('.pimpy_task_row[data-task-id=' + task_id + ']');
        var $task_btns = $('.pimpy_task', $task_rows);

        utils.form.button_loading($task_btns);

        $.post('/pimpy/tasks/update_status/',
            {
                task_id: task_id,
                new_status: status
            },
            function (data) {
                $task_btns.removeClass(btn_stati);
                $task_rows.removeClass(btn_stati);

                $task_btns.addClass(data.status);
                $task_rows.addClass('pimpy_status_' + data.status);
            }
        ).fail(function () {
            utils.flash.clear();
            utils.flash.new('Er ging iets mis, =(', 'danger');
        }).always(function () {
            $task_btns.button('reset');
        });
    });

    /* Editable Setting */
    $.fn.editable.defaults.mode = 'inline';

    /* Makes tasks content editable */
    $('.pimpy_editable').editable();

    $('.pimpy_editable_toggle').click(function () {
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

    $('.btn-filter').on('click', function (){
      var classes = this.attributes['data-hide'].value;

      if ($(this).hasClass('active')) {
        $('tr.pimpy_status_' + classes).hide();
      }
      else {
        $('tr.pimpy_status_' + classes).show();
      }
    });
});
