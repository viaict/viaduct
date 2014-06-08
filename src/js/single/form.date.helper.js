// Script start and end date updates
// When selecting a start date, you can only select end dates after that
$(document).ready(function() {
	// Resize textarea on startup
	$("textarea").flexible().trigger('keyup');

	// Check www.eyecon.ro/bootstrap-datepicke
	var nowTemp = new Date();
	var now = new Date(nowTemp.getFullYear(), nowTemp.getMonth(), nowTemp.getDate(), 0, 0, 0, 0);
	
	var checkin = $('#start_date').datepicker({
		onRender: function(date) {return date.valueOf() < now.valueOf() ? 'disabled' : '';}
	}).on('changeDate', function(ev) {

		var newDate = new Date(ev.date)
		newDate.setDate(newDate.getDate());
		checkout.setValue(newDate);
	
		checkin.hide();
		$('#end_date')[0].focus();

	}).data('datepicker');
	
	var checkout = $('#end_date').datepicker({
		onRender: function(date) {
		return date.valueOf() < checkin.date.valueOf() ? 'disabled' : '';
	}}).on('changeDate', function(ev) {checkout.hide();}).data('datepicker');

	$("#start_time").timepicker({showMeridian:false, defaultTime: "17:00"});
	$("#end_time").timepicker({showMeridian:false, defaultTime: "22:00"});
});
