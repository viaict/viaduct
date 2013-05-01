== site ==

* links (van het menu) moeten niet automagisch gegeneerd worden, moeten vanuit
een database geladen worden zodat je kan aangeven waaruit je menu bestaat.
    - MODULE: navigation
    - DOOR: BAS

    - als je nieuwe artikelen (Model: pages) aanmaakt moeten deze automagisch worden toegevoegd
    + je moet zelf links kunnen toevoegen (/verwijderen)
    ~ je moet externe links kunnen toevoegen.
        Werkt in de navbar, nog niet in het zijmenu.
    - Modules moeten in routes de parent/kind/nogmeerkind structuur aanhouden
      (bv. bestuur/bestuursblog/<int:blog_entry_id>)
      (bv. activities/activity/<int:activity_id>)

* sign-in/sign-up moet uitgebreid worden voor als je het wachtwoord vergeten bent.
    - MODULE: user
    - DOOR:
    - afhankelijkheid: mail-smtp-gegevens (flask-mail) moeten bekend zijn
    - Je krijgt een mailtje met een link om je wachtwoord opnieuw in te stellen.
    De link moet maar een bepaalde tijd geldig zijn en mag niet achterhaalbaar
    zijn.

* iets met pages aanmaken (gaat stephan nog even afmaken) als je foo/bar aanmaakt
maar foo bestaat nog niet moet foo ook aangemaakt worden. Dit heeft te maken met
de navigatiehierarchie.
    - DOOR: STEPHAN

* Page history op basis van diff. Er was ook nog iets met de revisions, dat je
page history hebt en terugkan

* Forms aanmaken. Er was een mooi systeem bedacht met 5 databasetabellen. Dit
bestond alleen nog maar in Stephans hoofd. Stephan moet even de tabellen
uittekenen.

* activiteitenbeheren.
    - DOOR: FABIEN
    + Activiteiten kunnen aangemaakt worden
    - Routing moet met goede structuur (zie navigation)
    - Activiteiten edit
    - Oude Plaatje verwijderen bij plaatje edit
    - Facebook event (google+) aanmaken
    - Attending op svia.nl
    - Facebook event comments scrapen
    - Google maps plugin (geolocate API : adres invoert)
    
* files uploaden. Uploaden kan al
    - er moet nog een beheringsysteem

* zoeksysteem

== PIMPY ==
    - DOOR: MAARTEN

== wiki (mediawiki) ==

== vacaturenbank ==

== boekensysteem ==

== tentamenbank ==
    - door: Bram

== mail ==
    - door: Ilja

== databases: ==
De databasemodellen die op veel plekken nodig zijn, zoals opleidingen en vakken,
moeten afgemaakt zijn zodat alle applicaties daar mee kunnen werken.



werknachten: met bier en pizza!
