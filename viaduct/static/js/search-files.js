$(function() {
	var $results = $('#file-search-results');

	$('#file-search-query').on('input', function() {
		var query = $(this).val();
		var filenames = $.get(sprintf('/files/search/%s/', query),
				function(data) {
					var filenames = data.filenames ? data.filenames : [];

					$results.empty();
					for (var i = 0; i < filenames.length; i ++) {
						var $li = $('<li></li>');
						$li.text(filenames[i]);
						$results.append($li);
					}
				});
	});
});
