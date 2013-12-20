$(document).ready(MakeOverlay());

$(document).ready(function() {
	$('#overlay_button').click(function() {
		RemoveOverlay();
	});
});

function RemoveOverlay() {
	$("#afs_overlay").remove();
}

function MakeOverlay() {
	$(function() {
		var docHeight = $(document).height();
		//$("body").append("<div id='afs_overlay' style='background:#000; font-family: Alegreya; color: #fff;'><div id='afs_image' style='margin:0 auto; padding-top:50px; width:400px;'><img src='afs.png' title='AFS, wat kan daar nou fout gaan?' /></div><div id='afs_text' style='margin: 0 auto; width: 500px; text-align: center;'><h1 style='text-transform: uppercase; font-size: 1.6em; text-align: center;'>Amsterdam Faculty of Science</h1><h2 style='text-weight:normal; text-align: center; font-style: italic; font-weight: normal;'>Wat kan daar nou fout gaan?</h2><p><!-- Voeg evt andere tekst toe -->Te veel. Deze megafaculteit wordt gebouwd op blind optimisme en lege argumentatie. Het huidige plan voor de Amsterdam Faculty of Science is ondermaats. Wij maken ons zorgen om de kwaliteitswaarborging van onderwijs en onderzoek. Zorgen om het verlies van identiteit, financiële haalbaarheid, grootte van studies en spreiding over twee locaties.</p><p>Deze zorgen hebben wij, studenten, keer op keer kenbaar gemaakt. Maar risico’s worden onder het tapijt geschoven en de medezeggenschapsraden genegeerd. Met als dieptepunt een nieuwe decaan voor een faculteit die er wat ons betreft niet komt. Wat moet er nog meer fout gaan?</p><button id='overlay_button' class='btn btn-red' style='background-color: rgb(215,9,41); color: #ffffff; margin-bottom:15px;'><strong>Ga verder naar de site</strong></button><br></div></div>");
		$("body").append(' <div id="weer_zon_leuke_overlay" style="background:#000; color: #fff;"> <h1 style="text-weight:normal; text-align: center; font-style: italic; font-weight: normal;">Kom nu naar CREA!</h1> <div id="afs_image" style="margin:0 auto; padding-top:50px; width:400px;"> <img src="afs.png" title="AFS, wat kan daar nou fout gaan?" /> </div> <div id="afs_text" style="margin: 0 auto; width: 500px; text-align: center;"> <p style="font-size: 18px;"> <!-- Voeg evt andere tekst toe --> Zonder dat er een woord gesproken is, is de vergadering 2 uur geschorst! Er zijn een half uur van te voren nieuwe stukken door het College van Bestuur vrijgegeven. Geen enkele vergadering in de wereld zou zo kort van te voren nog nieuwe stukken aannemen. Zorg dat er vandaag een beslissing wordt genomen en kom naar de Theaterzaal te CREA, Nieuwe Achtergracht 170. We eisen nu een beslissing! (Als het nodig is wordt de deur gebarricadeerd) Laat je stem horen! Kom in het rood!  </p> <button id="overlay_button" class="btn btn-red" style="width: 250px; margin-left: auto; margin-right: auto; background-color: rgb(215,9,41); color: #ffffff; margin-bottom:15px;"><strong>Ga verder naar de site</strong></button> <br> </div> </div> ');

		$("#weer_zon_leuke_overlay")
			.height(docHeight)
			.css({
				'position': 'absolute',
				'top': 0,
				'left': 0,
				'background-color': 'black',
				'width': '100%',
				'z-index': 5000,
				'height': '3000px'
			});
	});
}
