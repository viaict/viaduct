$(function() {
	var $results = $('#file-search-results');
	var $page_content = $('#content');

	var add_url = function() {
		var url = $(this).attr('href');
		$page_content.insertAtCaret(url);
		return false;
	}

	$('#file-search-query').on('input', function() {
		var query = $(this).val();
		var filenames = $.get(sprintf('/files/search/%s/', query),
				function(data) {
					var filenames = data.filenames ? data.filenames : [];

					$results.empty();
					for (var i = 0; i < filenames.length; i ++) {
						var filename = filenames[i];

						var $a = $('<a></a>');
						$a.attr('href', sprintf('/static/files/%s', filename));
						$a.text(filenames[i]);
						$a.on('click', add_url);

						var $li = $('<li></li>');
						$li.append($a);
						$results.append($li);
					}
				});
	});
});
