$(document).ready(function() {
	$('.mainblock').each(function() {
		var desired_height_text = $(this).css('min-height');
		var desired_height = parseInt(desired_height_text.
									substr(0, desired_height_text.length - 2));

		var actual_height = Math.floor($(this).height());

		if (actual_height > desired_height) {
			$main_block = $(this);

			$(this).css({'overflow': 'hidden',
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

			var $read_more_link = $('<a>Meer lezen</a>');
			$read_more_link.attr('href', '#');
			$read_more_link.on('click', function() {
				if (Math.floor($main_block.height()) == desired_height) {
					$main_block.animate({'height': sprintf('%dpx',
										actual_height + 20),
										'overflow': 'visible'});
					$(this).text('Minder lezen');
				}
				else {
					$main_block.animate({'overflow': 'hidden',
									'height': sprintf('%dpx', desired_height)});
					$(this).text('Meer lezen');
				}

				return false;
			});

			$read_more_div.append($read_more_link);

			$(this).prepend($read_more_div);
		}
	});
});

/* PimPy function
 * updates the task status
 */
function update_task_status($task_id, $new_status) {
	$.getJSON('/pimpy/tasks/update_status', {
		task_id: $task_id,
		new_status: $new_status
	}, function(data) {
		$id = 'pimpy_task'+$task_id;
		$('#'+$id).attr('class', "btn dropdown-toggle " + data.status);
	});
	return false;
}

function edit_task($task_id) {
	$.getJSON('/pimpy/tasks/edit', {
		task_id: $task_id
	}, function(data) {
	});
	return false;
}

function update_task($task_id, $task_name, $more_info,
	$deadline, $group, $users, $status) {
}
