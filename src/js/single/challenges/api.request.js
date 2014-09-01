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
		console.log( msg );
	});
	 
	request.fail(function( jqXHR, textStatus ) {
		alert( "Request failed: " + textStatus );
	});	
}

function update_challenge(){

}

function fetch_challenges(){

}

function create_submission(submission, challenge_id){
	var request = $.ajax({
		url: "/challenges/api/create_challenge",
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