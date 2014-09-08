$(document).ready(function(e){

	$("form.challenge_submission").submit(function (e) {
	    e.preventDefault();
	    submission = $(this).find("input.submission").val();
	    challenge_id = $(this).attr("via-challenge-id"); 
	    create_submission(submission, challenge_id);
	    $(this).find("input.submission").val("");
	});

	$("form#edit_challenge").submit(function (e) {
	    e.preventDefault();
	    name = $(this).find("input#name").val();
	    description = $(this).find("textarea#description").val();
	    hint = $(this).find("input#hint").val();
	    start_date = $(this).find("input#start_date").val();
	    end_date = $(this).find("input#end_date").val();
        parent_id = 0
        weight = $(this).find("input#weight").val();
        type = "Text";
        answer = $(this).find("input#answer").val();

	    create_challenge(name, description, hint, start_date, end_date,
                        parent_id, weight, type, answer)
	    $(this).find("input.submission").val("");
	});
});

function create_challenge(name, description, hint, start_date, end_date,
                        parent_id, weight, type, answer){
	var request = $.ajax({
		url: "/challenge/api/create_challenge",
		type: "GET",
		data: { name : name, description : description, hint : hint, start_date : start_date, end_date : end_date,
                        parent_id : parent_id, weight : weight, type : type, answer : answer },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		alert( msg );

        $("#edit_challenge").find("input[type='text']").val("");
        $("#edit_challenge").find("textarea").val("");
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});	
}


function update_challenge(){

}

function fetch_challenges(){

}

function fetch_challenge(challenge_id){
	var request = $.ajax({
		url: "/challenge/api/fetch_challenge",
		type: "GET",
		data: { challenge_id : challenge_id },
		dataType: "JSON"
	});

	request.done(function( msg ) {
		$("#edit_challenge").find("input#name").val(msg.challenges.name);
	    $("#edit_challenge").find("textarea#description").val(msg.challenges.description);
	    $("#edit_challenge").find("input#hint").val(msg.challenges.hint);
	    $("#edit_challenge").find("input#start_date").val(msg.challenges.start_date);
	    $("#edit_challenge").find("input#end_date").val(msg.challenges.end_date);
        $("#edit_challenge").find("input#weight").val(msg.challenges.weight);
        $("#edit_challenge").find("input#answer").val(msg.challenges.answer);
		console.log(msg.challenges)
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});

}

function create_submission(submission, challenge_id){
	var request = $.ajax({
		url: "/challenge/api/new_submission",
		type: "GET",
		data: { challenge_id : challenge_id, submission : submission },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		update_user_points(user_id);
		alert(msg);

		if(msg == "Approved"){
			var that = $("#challenge_" + challenge_id).closest(".challenge_todo");
			$("#before_done_challenges").before(that);
			$(that).before("<hr>");
			$("#challenge_" + challenge_id).parent().siblings(".challenge_description").removeClass("col-md-5");
			$("#challenge_" + challenge_id).parent().siblings(".challenge_name").removeClass("col-md-3");
			$("#challenge_" + challenge_id).parent().siblings(".challenge_description").addClass("col-md-6");
			$("#challenge_" + challenge_id).parent().siblings(".challenge_name").addClass("col-md-5");
			$("#challenge_" + challenge_id).parent().remove();

		}
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});
}

function validate_submission(submission_id){
	var request = $.ajax({
		url: "/challenge/api/validate_submission",
		type: "GET",
		data: { submission_id : submission_id },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		console.log( msg );
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});
}

function get_points(user_id){
	var request = $.ajax({
		url: "/challenge/api/get_points",
		type: "GET",
		data: { user_id : user_id },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		console.log( msg );
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});

}

function update_user_points(user_id){
	var request = $.ajax({
		url: "/challenge/api/get_points",
		type: "GET",
		data: { user_id : user_id },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		$("#user_points").html(msg);
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});
}

function move_to_done(challenge_id){

}