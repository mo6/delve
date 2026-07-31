# Vrije-tekst rubrics (PoC, Nederlands)

De Nederlandse tegenhanger van `rubrics.md`: dezelfde drie vragen, nu in het Nederlands, om te
testen of het lokale model even goed in het Nederlands beoordeelt als in het Engels. Delve levert
elke pack in `en` en `nl`, dus de beoordelaar moet beide talen aankunnen.

Vorm en regels volgen [docs/PHASE2.md](../../docs/PHASE2.md) §4 en de stijlregels: tutoyeren (`je`,
nooit `u`), zinsvorm in koppen, geen kastlijntjes. De accept-set voedt zowel de LLM-prompt als de
trefwoord-fallback.

### Een onverwacht bericht geeft je het gevoel dat je nu meteen moet handelen. In een of twee woorden, welk gevoel is dat, en waarom is het het belangrijkste wapen van de aanvaller?

- ?answer: urgentie, tijdsdruk, haast, gejaagdheid, paniek, het gevoel opgejaagd te worden
- ?reject: angst om ontslagen te worden, nieuwsgierigheid, hebzucht

> Urgentie is de hefboom, want nadenken is wat de aanval kapotmaakt. De mail wil dat je in
> beweging komt voordat je de ene ding controleert dat hem zou verraden. Kunstmatige tijdsdruk,
> plus een reden om niet te verifiëren, is de vingerafdruk; de rest is decor.

### Er komt een mail van het echte, juiste adres van een collega met de vraag een bijlage te openen. Er is niets mis met het adres. Waarom is dat in één zin niet genoeg om het te vertrouwen?

- ?answer: het account kan gehackt zijn, accountovername, hun account is overgenomen, een juist adres bewijst alleen dat het van dat account komt niet dat zij het stuurden
- ?reject: het is altijd veilig, het mailsysteem markeert het als intern

> Een juist afzenderadres bewijst dat de mail van dat account komt, niet dat je collega hem
> stuurde. Accountovername is precies het geval waarin elke adrescontrole slaagt, en daarom kan
> "controleer de afzender" niet de hele gewoonte zijn.

### De hele scène van de bewaker draait om één vraag over de kokosnoot. Wat wil hij weten?

- ?answer: waar je hem vandaan hebt, hoe je een tropische kokosnoot in Engeland kreeg, de herkomst van de kokosnoot, de bevoorradingsketen, zijn herkomst
- ?reject: of de koning dapper is, of de queeste heilig is

> Niet "is de koning dapper", niet "is de queeste heilig": alleen waar de kokosnoot vandaan
> kwam. De eenvoudigste rekwisiet heeft een probleem met zijn bevoorradingsketen, en één eerlijke
> vraag over herkomst rafelt het hele idee uit elkaar.
