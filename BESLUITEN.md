Ik mail dit soort dingen ook altijd.

## DOCUMENTATIE
Documenteer aub iig op de volgende manier: http://www.python.org/dev/peps/pep-0257/ (de standaard manier om python te documenteren).

Dit kunnen we gaan gebruiken om automagische documentatie te genereren.

Globale module-specifieke informatie zetten we dan bovenaan de viewer.

Uiteindelijk zouden we ook oude modules langs moeten gaan om deze comments toe te voegen en zo een complete documentatie van viaduct te krijgen (al hoop ik dat sommige van ons dat gewoon al gedaan hebben). Voor nu is het echter belangrijk dat nieuwe code hier iig een beetje aan voldoet.

## TAAL
Alle taal in de code is Engels. Vertalingen worden gedaan dmv Flask-Babel.

Alle strings dienen worden ingevoerd met de (lazy_)gettext functie.

```python
    from flask_babel import _ (In views)
    from flask_babel import lazy_gettext as _ (In models en Forms)
```

## TABS EN VIM ENZO
In vim: `set noexpandtab' en `set sw=4 ts=4 sts=0'

## DATABASE-AANPASSINGEN
Als je database-aanpassingen doet, mail dit dan naar ict@svia.nl zodat we bij
updates de database online ook aan kunnen passsen (en niet hoeven zoeken naar
gekke errors etc).


