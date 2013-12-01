## General
* talen module voor multi-language site

## sign-in/sign-up
* wat is er aan de hand als je je inloggegevens kwijt bent?
* misschien inloggegevens van CAS gebruiken. De zelfde authenticatie die datanose etc gebruikt. Eerst mailen of het mag. Dit is een ingrijpende verandering, dus gaat voorlopig niet gebeuren (wss).
* Voeg jaartal van begin studie toe aan user
* Zorg dat mensen die zich aanmelden met een jaartal van voor 2013 automatisch betaald zijn.

## errorpaginas, 'BRAM'
* zoals 403 mooier maken

## User paginas
* Foto uploaden per profiel

## Forms, 'FABIEN'
* tutorial
* Formulier aanmaken via modal / ajax, dat je niet eerst je formulieren hoeft te maken en dan pas kan selecteren (GAAT NIET GEBEUREN)
* Mooier resultaten zien (nu zie je puur $POST data)
* Automatisch herkennen of formulier al is ingevuld / pre-vullen oid (of uitklapbaar zeg maar, dat je niet meteen in scherm hebt)
* Paar extra `shortcuts` en shortcuts duidelijker vermelden ( Poep | user geeft je bijv. student nr / email / naam / studie die je een gebruiker wilt laten invullen (GAAT NIET GEBEUREN)
* Toevoegen dat wanneer formulier wordt ingevuld, het de gebruiker data ook update als die zou ontbreken (bijv. telefoon nummer, wordt het nu ingevuld dan is het wel chill om die te blijven houden)
* Mogelijkheid tot entries deleten

## wiki-systeem
* zoeksysteem (zie zoekmodule)
* categorieen

## pimpy
* get_tasks querys toch nog maar wat efficienter maken
* tasks niet standaard op edit laten staan

## boekensysteem
Is nu nog heel basic, we kunnen boeken toevoegen, een bepaalde stock, boeken verkopen (stock --) maar er word niet gechekct of er nog is. Er wordt niet gefilterd (geen zoekfunctie). Er is niet zo iets als boekenpaketten. Er moeten nog database entries komen voor bij welk jaar een boek hoort.
Heeft pas voor het tweede semester prioriteit.

## spelfout/taal-consistentie check doen
Alles moet eigenlijk even nagelopen worden of het allemaal 1 taal is en spelfoutloos.

## Tentamenbank, Victors verzoeken (Mailonderwerp `Tentamenbank`, tijdspostzegel `Sun, Sep 15, 2013 at 3:35 PM`) 'BRAM'
* De vakken aan een studie te koppelen (dus dat er niet perongeluk vakken bij de verkeerde studie terecht kunnen komen);
* De vakken, studies, tentamens op alfabetische volgorde te zetten;
* De titelsuggestie voor het tentamen (bij nieuw tentamen) aan te passen naar de standaard (zie doc).

## documentatie
* systeem opzetten wat de documenatie voor viaduct organiseert
* alle modules etc documenteren
* Tutorial maken voor wiki-systeem wanneer het er is

## bugs/FIXMEs
* current user heeft id = 0 lokaal maar is None op de server. Het ligt iig niet aan verschillende versies van Flask. Verder kon ik (Inja) niet echt iets vinden. Daarom moet je altijd eerst checken op current_user != None en daarna pas op id == 0 voor een niet ingelogde user.
* navigation, je kan nog geen paginas deleten (check of een entry geen children heeft faalt altijd).
* (files uploaden) permissies van het mapje waar we naar uploaden niet op 777
zetten, 'BAS' - Het lijkt alleen te werken als de 'others' execute recht
hebben.. Kan er eigenlijk niet zo veel aan doen..
zetten, IS NIET GELUKT, REQUIRE LINUX GOD
* als je geen rechten hebt en doorverwezen bent na het inloggen zou het mooi
zijn als je daarna wel op de pagina komt die je oorspronkelijk probeerde te
bereiken 'BAS'
* paginas waar je geen rechten toe hebt verwijderen uit het menu (zoals admin)
* Een aparte groep voor ingelogde users
* CAS gebruiken?

## mail
* alles (sorry ik, maarten, weet niet echt wat hier moet gebeuren :O )? 'JOEY'

## vacaturenbank, 'BAS'
* oh yeah

## zoekmodule/api
Een dynamische module die gebruikt kan gaan worden in de tentamenbank,
vacaturenbank en de wiki. Mischien zelfs pimpy. DONE, maar moet nog getest
worden 'MAARTEN'

## Export module
Een module om lijsten te exporteren

## Ideal
Ideal betalen bitches 'TIJMEN'

Je geeft op welke tabellen en welke kolommen doorzocht moeten worden. `tijmen zwaan` als query moet matchen op
een user terwijl de kolomen firstname en lastname zijn.

## FAVICON
er moet wel een favicon op de site komen

## permissions
In viaduct hebben we modules, zoals pimpy, group, user etc. Kijk maar naar svia.nl/groups en dan edit permissions van administrator voor een overzicht van de modul die we hebben. We hebben ook een module waarin je kan zetten welke groups welke modules mogen lezen of lezen en schrijven en het zou chill zijn als je deze kan verbeteren.

Vorige keer was dit vrij snel bij elkaar gehackt maar we willen natuurlijk dat de modules die we in viaduct stoppen automagisch getoond worden, en aanpasbaar zijn (indien juiste rechten). Nu is het zo dat je zelf de naam van een module moet toevoegen.

Een verbetering is als module_permission dit zelf bijhoudt. Hiervoor moet het dus dynamisch kunnen zien welke modules in viaduct zitten OF we moeten zorgen dat modules zichzelf ergens registreren zodat de module_permission daar kan zien welke modules er allemaal zijn.

Module permissie moet niet overridden worden door page permission. (bestuur moet altijd toegang hebben tot page bijvoorbeeld)

## user page
* kunnen zien waar je allemaal voor bent ingeschreven
* een functie toevoegen voor 'heeft betaald' als permissie. (dus content voor enkel leden)


