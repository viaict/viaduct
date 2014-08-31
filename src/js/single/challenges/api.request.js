function create_challenge(){

}

function update_challenge(){

}

function fetch_challenges(){

}

function create_submission(submission, challenge_id){
	var request = $.ajax({
		url: "/challenges/api/validate_submission",
		type: "GET",
		data: { challenge_id : challenge_id, submission : submission },
		dataType: "html"
	});
	 
	request.done(function( msg ) {
		console.log( msg );
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});
}

function validate_submission(submission_id){
	var request = $.ajax({
		url: "/challenges/api/validate_submission",
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

function fetch_points(){

}