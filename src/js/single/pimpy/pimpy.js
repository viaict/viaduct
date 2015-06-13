$(function () {
    'use strict';

    var btn_stati = 'btn-info btn-warning btn-success btn-danger';

    /* updates the task status */
    $('.pimpy_task').attr('data-loading-text', 'BITTE WARTEN!');

    $('.pimpy_status').click(function () {
        var $this = $(this);

        var $task_btn = $this.parents('div.btn-group').children('.pimpy_task');
        $task_btn.button('loading');

        var $task_row = $this.parents('tr');

        var task_id = $this.data('task-id');
        var status = $this.data('status-id');

        $.getJSON('/pimpy/tasks/update_status', {
            task_id: task_id,
            new_status: status
        }, function (data) {
            $task_btn.removeClass(btn_stati);
            $task_row.removeClass(btn_stati);

            $task_btn.addClass(data.status);
            $task_row.addClass('pimpy_status_' + data.status);
        }).fail(function () {
            flash('Er ging iets mis, =(', 'danger');
        }).always(function () {
            $task_btn.button('reset');
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
