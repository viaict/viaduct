$(function () {
    'use strict';

    /* updates the task status */
    $('.pimpy_status').click(function () {
        var task_id = $(this).data('task-id');
        var status = $(this).data('status-id');

        $.getJSON('/pimpy/tasks/update_status', {
            task_id: task_id,
            new_status: status
        }, function (data) {
            $('#pimpy_task' + task_id).attr('class',
                'btn dropdown-toggle ' + data.status);
            $('#pimpy_task_row_' + task_id).attr('class',
                'pimpy_status_' + data.status);
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
