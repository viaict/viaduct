## sign-in/sign-up
* wat is er aan de hand als je je inloggegevens kwijt bent?

## errorpaginas, 'BRAM'
* zoals 403 mooier maken

## Forms, 'FABIEN'
* tutorial
* Formulier aanmaken via modal / ajax, dat je niet eerst je formulieren hoeft te maken en dan pas kan selecteren (GAAT NIET GEBEUREN)
* Mooier resultaten zien (nu zie je puur $POST data)
* Automatisch herkennen of formulier al is ingevuld / pre-vullen oid (of uitklapbaar zeg maar, dat je niet meteen in scherm hebt)
* Paar extra `shortcuts` en shortcuts duidelijker vermelden ( Poep | user geeft je bijv. student nr / email / naam / studie die je een gebruiker wilt laten invullen (GAAT NIET GEBEUREN)
* Toevoegen dat wanneer formulier wordt ingevuld, het de gebruiker data ook update als die zou ontbreken (bijv. telefoon nummer, wordt het nu ingevuld dan is het wel chill om die te blijven houden)

## wiki-systeem
* zoeksysteem (zie zoekmodule)
* categorieen

## pimpy, 'TIJMEN'
* tasks aanpasbaar maken
* naar de parser kijken (crazy ass fouten)
* tussenscherm na het uploaden van notulen

## boekensysteem
Is nu nog heel basic, we kunnen boeken toevoegen, een bepaalde stock, boeken verkopen (stock --) maar er word niet gechekct of er nog is. Er wordt niet gefilterd (geen zoekfunctie). Er is niet zo iets als boekenpaketten. Er moeten nog database entries komen voor bij welk jaar een boek hoort.
Heeft pas voor het tweede semester prioriteit.

## spelfout/taal-consistentie check doen
Alles moet eigenlijk even nagelopen worden of het allemaal 1 taal is en spelfoutloos.

## documentatie
* systeem opzetten wat de documenatie voor viaduct organiseert
* alle modules etc documenteren

## bugs/FIXMEs
* current user heeft id = 0 lokaal maar is None op de server, 'MAARTEN'
* navigation, je kan nog geen paginas deleten (check of een entry geen children heeft faalt altijd).
* (files uploaden) permissies van het mapje waar we naar uploaden niet op 777 zetten, 'BAS'


## mail
* alles?

## vacaturenbank, 'BAS'
* oh yeah

## zoekmodule
Een dynamische module die gebruikt kan gaan worden in de tentamenbank, vacaturenbank en de wiki. Mischien zelfs pimpy.

Je geeft op welke tabellen en welke kolommen doorzocht moeten worden. `tijmen zwaan` als query moet matchen op
een user terwijl de kolomen firstname en lastname zijn.

## permissions
In viaduct hebben we modules, zoals pimpy, group, user etc. Kijk maar naar svia.nl/groups en dan edit permissions van administrator voor een overzicht van de modul die we hebben. We hebben ook een module waarin je kan zetten welke groups welke modules mogen lezen of lezen en schrijven en het zou chill zijn als je deze kan verbeteren. 

Vorige keer was dit vrij snel bij elkaar gehackt maar we willen natuurlijk dat de modules die we in viaduct stoppen automagisch getoond worden, en aanpasbaar zijn (indien juiste rechten). Nu is het zo dat je zelf de naam van een module moet toevoegen.

Een verbetering is als module_permission dit zelf bijhoudt. Hiervoor moet het dus dynamisch kunnen zien welke modules in viaduct zitten OF we moeten zorgen dat modules zichzelf ergens registreren zodat de module_permission daar kan zien welke modules er allemaal zijn. 
