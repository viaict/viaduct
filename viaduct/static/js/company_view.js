'use strict'
/*didn't work*/

// $(function() {

// 	/* Load contact dynamic per location. */
// 	$('#location_id').on('change', function() {
// 		var $this, location_id, $contact_select;

// 		$this = $(this);
// 		location_id = $this.val();

// 		$contact_select = $('#contact_id');
// 		$contact_select.empty();
// 		$contact_select.val('');

// 		$.getJSON('/locations/' + location_id + '/contacts/', function(data) {
// 			var contacts;

// 			contacts = data.contacts;
// 			for (var i = 0; i < contacts.length; i ++) {
// 				var contact, $option;

// 				contact = contacts[i];

// 				$option = $('<option></option>');
// 				$option.val(contact.id);
// 				$option.text(contact.name);

// 				$contact_select.append($option);
// 			}

// 			if (contacts.length > 0)
// 				$contact_select.val(contacts[0].id);
// 		});
// 	});
// });