$(document).ready(function() {
	$('div.expander').expander({
		slicePoint: 1600,
		expandText: "lees meer",
		userCollapseText: "lees minder",
		expandSpeed: 1000,
		collapseSpeed: 1000,
	});
});

/* PimPy function
 * updates the task status
 */
function update_task($task_id, $new_status) {
	$.getJSON('/pimpy/tasks/update', {
		task_id: $task_id,
		new_status: $new_status
	}, function(data) {
		$id = 'pimpy_task'+$task_id;
		$('#'+$id).attr('class', "btn dropdown-toggle " + data.status);
	});
	return false;
}
