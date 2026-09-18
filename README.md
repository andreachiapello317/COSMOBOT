# StelleBot

Bot Telegram in Python (async, `python-telegram-bot` v21+) su **oroscopo, astrologia, pianeti, stelle e astronomia**.

Il tono è chiaro, curioso e un po’ ironico: planetario tascabile, non biglietto romantico. **Oroscopi, fasi lunari, efemeridi e foto NASA arrivano da API live.** Nel codice non ci sono testi di fatti o previsioni copiati a mano.

Repository GitHub: [andreachiapello317/COSMOBOT](https://github.com/andreachiapello317/COSMOBOT)

## Cosa fa

| Comando | Effetto | Fonte live |
| --- | --- | --- |
| `/start` | Presenta il bot e i comandi | — |
| `/tema` | Tema natale guidato: data, ora, luogo → Big Three, pianeti, case, aspetti | [CosmyDay `/natal`](https://cosmyday.com/api-docs) |
| `/oroscopo [segno]` | Chiede giorno / settimana / mese con i bottoni. Senza segno usa **Bilancia** | [freehoroscopeapi.com](https://freehoroscopeapi.com) daily, weekly, monthly |
| `/oracoli` | Hub del reparto: tradizionali + mazzi COSMOBOT | — |
| `/lettura` | Scrivi la situazione, poi scegli tarocchi / I Ching / rune / Lenormand / sorprendimi | riusa i rituali |
| `/tarocchi` | 1/3 carte, amore, lavoro, domanda, carta del giorno, Croce Celtica | [freehoroscopeapi.com/tarot](https://freehoroscopeapi.com/tarot) |
| `/iching` | Consultazione I Ching: domanda, sei lanci, esagramma, linee mutevoli, trasformato | [Wilhelm 1924 JSON](https://github.com/jesshewitt/i-ching) (libro pubblico live) |
| `/sibille` | Petit Lenormand 1/3/5/9 carte + combinazioni | dataset `services/lenormand.py` |
| `/sino` | Sì/No simbolico (tarocco, runa o I Ching) | stesse fonti, non un verdetto |
| `/archetipi` `/animali` `/simboli` `/elementi` `/oracoloplanetario` | Mazzi originali COSMOBOT | `services/oracles.py` |
| `/oracololunare` | Messaggio coerente con la fase | sunrisesunset.io + testo simbolico |
| `/oracolodande` | Una domanda introspettiva, poi rifletti | dataset interno |
| `/asteroidi` | Menu: NEO vicini, asteroidi noti (Wikipedia), o Ceres/Vesta/Pallade/Giunone nel tema | [NASA NeoWs](https://api.nasa.gov) + [Horizons](https://ssd.jpl.nasa.gov/horizons) + Wikipedia |
| `/meteore` | Prossimo sciame e calendario dei picchi | [Skytime meteor-showers](https://skytime.live/api/docs) |
| `/spazio` | Briefing del giorno: Luna, pianeti, eventi, sciami, cielo osservabile | CosmyDay events + Skytime + skymap.sh + sunrisesunset.io |
| `/osserva` | Elenco dettagliato da una città (Luna, pianeti, costellazioni) | [skymap.sh](https://skymap.sh) + geocoding CosmyDay |
| `/cielo [città]` | Cosa vedi **ADESSO**: mappa testuale, ↑/↓/👁, città memorizzata | skymap.sh + sunrisesunset.io + Skytime |
| `/stelle` | Menu stelle: casuale, del giorno, visibili ora, tipi (giganti, nane, pulsar…) | Wikipedia/Wikidata + skymap.sh; APOD resta un bottone |
| `/costellazioni` | Del giorno, casuale, visibili stasera, schede mitologiche | Wikipedia + asterismi skymap.sh |
| `/nani` | Plutone, Cerere, Eris, Haumea, Makemake | Wikipedia + Wikidata |
| `/comete` | Selezione (Halley, 67P, NEOWISE…) | Wikipedia — non il dump JPL |
| `/profondo` | Messier, NGC, nebulose, quasar, SN 1987A | Wikipedia + Wikidata |
| `/pianeta` | Scheda di un pianeta (massa, diametro, gravità, missioni) | Wikipedia + Wikidata + NASA Images |
| `/lune` | Europa, Titano, Encelado e le altre | Wikipedia + Wikidata |
| `/buchineri` | Cos'è un buco nero + Sgr A*, M87*, Cygnus X-1 | Wikipedia + NASA Images |
| `/galassia` | Via Lattea, Andromeda, confronto distanze | Wikidata P2583 |
| `/eclissi` | Prossima solare, prossima lunare, countdown, picco | [Skytime eclipses](https://skytime.live/api/docs) |
| `/alba` | Alba, tramonto, durata, crepuscolo civile/astronomico | sunrisesunset.io (`/sole` è lo stesso) |
| `/missioni` | Artemis, Webb, Clipper, JUICE, Voyager… | Wikipedia |
| `/astronauta` | Schede di astronauti storici | Wikipedia |
| `/satelliti` | Hubble, Webb, Chandra, ISS | Wikipedia + WTIA per la ISS |
| `/sonde` | Voyager, New Horizons, Cassini, Juno… | Wikipedia |
| `/impara` | Mini-lezioni: Sistema Solare, stelle, buchi neri, galassie, missioni, esopianeti | Wikipedia |
| `/quiz` | Facile / medio / difficile / esperto + classifica personale | Wikipedia, Wikidata, NASA TAP |
| `/mondi` | Esploratore: filtri TAP, mondo del giorno, casuale, salvataggi, vita, missioni→mondi | NASA TAP + Wikipedia |
| `/sistemi` | Alberi di sistemi (TRAPPIST-1, binari, multipli, HZ) | NASA TAP `hostname` |
| `/cosmo` | Mappa stelle / sistemi / mondi / galassie / nebulose / buchi neri | cataloghi già usati |
| `/sistema` | Scelta: Sistema Solare (Wikidata) o sistemi extrasolari (TAP) | Wikipedia + TAP |
| `/esopianeta` | Menu: casuale, simile alla Terra, infernale, estremo, oceanico (modello), recente | [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu) tabella `ps` |
| `/abitabile` | Candidati in zona abitabile (modello Teq/raggio, non vita) | stesso archivio TAP |
| `/vita` | Come cerchiamo la vita: oceani, SETI, biosignature | Wikipedia |
| `/specchio` | Domanda introspettiva + riflessione | pratica simbolica |
| `/rituale` | Intenzione / rilascio / chiusura secondo la fase lunare | fase live sunrisesunset.io |
| `/random` | Pesca casuale: tarocco, I Ching, runa, pianeta, missione, oggetto | le API già usate |
| `/missione` | Missione del giorno (Orione, Luna, APOD, quiz…) | calendario locale |
| `/rune` | Rituale Elder Futhark: domanda, 1 o 3 rune, upright/reversed | dataset interno (`services/runes.py`) |
| `/iss` | Posizione live della ISS + mappa | [Where the ISS at?](https://wheretheiss.at/w/developer) |
| `/cosmico` | Un pezzo da ogni mondo: te stesso, cielo, carta, esopianeta, missione | API in parallelo |
| `/esplora` | I sette mondi | — |
| `/pietre` | Mondo delle pietre: enciclopedia, laboratorio, collezione, museo | catalogo locale + Wikipedia |
| `/pietra` | Oracolo simbolico delle pietre (non è mineralogia) | catalogo locale |
| `/domanda` | Una domanda, poi scegli tarocchi, I Ching o rune | riusa i workflow esistenti |
| `/eventi` | Prossimi eventi del cielo | CosmyDay + Skytime |
| `/sole` | Come `/alba` | sunrisesunset.io |
| `/transiti` | Cielo di oggi sul tema salvato | CosmyDay |
| `/luna` | Fase, illuminazione, moonrise/moonset + spiegazione del giorno | [sunrisesunset.io](https://sunrisesunset.io/api/) + [CosmyDay](https://api.cosmyday.com/content/moon) |
| `/pianeti` | Posizioni attuali dei pianeti principali sopra Roma | [CosmyDay `/natal`](https://cosmyday.com/api-docs) (Swiss Ephemeris) |
| `/apod` | Astronomy Picture of the Day (foto o video) | [NASA APOD](https://api.nasa.gov) |
| `/aiuto` | Elenco comandi | — |

Se scrivi solo il nome di un segno (`vergine`, `Leo`, `scorpione`…) viene trattato come `/oroscopo`. Puoi anche scrivere `/oroscopo vergine settimanale` per saltare la scelta.

`/tema` (o `/natale`) chiede data, ora e città una alla volta, geocodifica con CosmyDay e calcola Sole, Luna, Ascendente, pianeti, case e aspetti. Puoi salvare il tema e poi vedere i transiti di oggi rispetto alla carta.

`/tarocchi` (o `/tarot`) è una lettura guidata: scegli lo spread, (se serve) scrivi la domanda, poi **PESCA LE CARTE**. L’API decide quali carte escono; dritta/rovesciata è casuale; i testi sono i significati ufficiali, tradotti e letti insieme. Lo storico resta sul server (su Render free può azzerarsi al riavvio).

`/iching` (o `/yijing`) è un rituale diverso: prima la domanda, poi **SONO PRONTO**, conferma, **LANCIA LE MONETE**. Le sei linee si costruiscono dal basso verso l’alto (metodo delle tre monete: 6/7/8/9). Il bot mostra esagramma, linee mutevoli e — se ci sono — l’esagramma trasformato. I testi (giudizio, immagine, linee) arrivano dal libro Wilhelm 1924 in JSON pubblico e vengono tradotti; le monete si lanciano in locale.

`/asteroidi` apre un menu: **vicini alla Terra** (NASA NeoWs), **asteroidi noti** (Wikipedia: Vesta, Bennu…), oppure **nel tema natale** (Ceres, Vesta, Pallade, Giunone da Horizons). Per il tema serve una carta salvata o appena calcolata.

`/meteore` mostra il prossimo sciame (picco e ZHR) e quelli in arrivo. `/spazio` è il briefing del giorno. `/osserva` chiede la città e elenca cosa c’è sopra l’orizzonte. `/cielo` è la mappa testuale di **adesso** (↑ sopra, ↓ sotto, 👁 mag ≤ 6), con città memorizzata; `/cielo Milano` geocodifica al volo. `/stelle` e `/costellazioni` mescolano schede Wikipedia e visibilità live. `/nani`, `/comete` e `/profondo` sono cataloghi curati: JPL Horizons ha milioni di oggetti, qui non li scarico in blocco.

`/mondi` è l'esploratore: filtri TAP (terrestri, oceanici come modello, ghiacciati, infernali, multi-stella, orbite eccentriche…), mondo del giorno, casuale, sistemi, «e se ci fosse vita?» (Wikipedia vs speculazione), missioni→corpi, e una lista di mondi salvati sul server. `/sistemi` apre gli alberi (TRAPPIST-1 incluso). `/cosmo` sta sopra: stelle, sistemi, mondi, galassie, nebulose, buchi neri. I mondi **generati** sono etichettati come finti.

`/esopianeta` apre i filtri NASA (casuale, simile alla Terra, infernale, estremo, oceanico come **modello**, recente). `/abitabile` è il filtro zona abitabile: Teq e raggio, **non** una dichiarazione di vita. `/specchio` e `/rituale` sono pratiche simboliche, presentate come tali: stanno in 🔮 ORACOLI / TE STESSO, non in 🔭 CIELO.

Il mondo **🔭 CIELO** è astronomia reale. Il mondo **🔮 ORACOLI** è esperienza simbolica. Il mondo **💎 PIETRE** è autonomo: mineralogia e geologia da catalogo pubblico, folklore tenuto a parte. Non si mescolano.

`/pietre` apre l’universo: schede (scienza / geologia / storia / simbolismo), colori, ambienti, laboratorio guidato, confronto, giochi, museo, collezione, pietre dallo spazio. `/pietra` è l’oracolo dichiarato come gioco. Una foto non sostituisce un’analisi; niente prezzi inventati. La rarità è di catalogo, non una quotazione.

`/start` apre una home a **sette mondi** (te stesso, divinazione, cielo, mondi, vita, missioni, pietre) più **COSMICO** e **RANDOM**. `/esplora` è la stessa mappa. `/rune` è locale (24 rune Elder Futhark). `/iss` legge Where the ISS at? senza chiave. `/cosmico` prende un pezzo da ogni mondo: se una API cade, le altre restano.

Su ogni schermata (tranne la home) c’è **⬅️ Indietro**: torna al menu precedente, senza ripassare da Inizio. **🏠 Inizio** resta sempre disponibile.

In chat il bot tiene **un solo messaggio**: ogni comando modifica (o sostituisce) la risposta precedente, senza accodarne di nuove. Il comando che hai scritto (`/luna`, `/oroscopo`…) viene cancellato appena la risposta è pronta.

I feed in inglese vengono tradotti in italiano al volo. Se un’API non risponde il bot dice:

> Le stelle sono temporaneamente offline ✨ riprova tra poco

---

## Requisiti

- Python 3.10 o superiore (consigliato 3.11/3.12)
- Un bot creato con [@BotFather](https://t.me/BotFather) e il relativo token

## Test locale (polling)

Quando **non** c’è `WEBHOOK_URL` il bot usa il long polling: va bene sul portatile, senza HTTPS pubblico.

```bash
git clone https://github.com/andreachiapello317/COSMOBOT.git
cd COSMOBOT

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Apri `.env` e imposta almeno:

```env
TELEGRAM_BOT_TOKEN=123456:il-token-di-BotFather
# WEBHOOK_URL va lasciato vuoto in locale
```

Opzionale ma consigliato: una chiave NASA gratuita su [api.nasa.gov](https://api.nasa.gov) (la `DEMO_KEY` ha un tetto basso di richieste).

```env
NASA_API_KEY=la_tua_chiave
```

Avvio:

```bash
python bot.py
```

Nei log deve comparire `Avvio in modalità POLLING`. Apri Telegram, cerca il bot, manda `/start` e prova `/oroscopo`, `/luna`, `/pianeti`, `/apod`, `/stelle`.

Per fermarlo: `Ctrl+C`.

---

## Deploy su Render (webhook, 24/7)

Render espone un URL HTTPS e inietta la variabile `PORT`. Il bot, se trova `WEBHOOK_URL`, registra il webhook su Telegram e ascolta su `0.0.0.0:$PORT`.

### 1. Metti il codice su Git (GitHub/GitLab)

Il servizio Render parte da un repository Git.

### 2. Crea un Web Service

1. [Dashboard Render](https://dashboard.render.com) → **New** → **Web Service**
2. Collega il repo
3. Impostazioni:

| Campo | Valore |
| --- | --- |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python bot.py` |
| Instance | Free va bene per un bot personale (si addormenta dopo inattività: il primo messaggio dopo il sonno può tardare ~50s) |

Lascia **vuoto** *Health Check Path*: Render controllerà che la porta sia aperta (TCP). Non usare `/` come health check HTTP: il server di `python-telegram-bot` accetta i POST di Telegram sul path del webhook, non una homepage.

### 3. Variabili d’ambiente su Render

**Environment** → **Add Environment Variable**:

| Variabile | Obbligatoria | Valore |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | sì | token di @BotFather |
| `WEBHOOK_URL` | sì, in produzione | URL pubblico del servizio, **senza slash finale**. Esempio: `https://stellebot.onrender.com` (lo vedi dopo il primo deploy, poi fai **Manual Deploy** se l’hai aggiunto dopo) |
| `PORT` | no | Render la fornisce da solo. Non impostarla a mano. |
| `WEBHOOK_PATH` | no | default `webhook`. Telegram chiamerà `{WEBHOOK_URL}/{WEBHOOK_PATH}` |
| `WEBHOOK_SECRET` | consigliata | stringa casuale (lettere, numeri, `_`, `-`). Telegram la rimanda in header, così nessuno può fingere update. |
| `NASA_API_KEY` | consigliata | chiave da api.nasa.gov; se manca si usa `DEMO_KEY` |

Esempio concreto:

```text
TELEGRAM_BOT_TOKEN=123456789:AA-xxxxxxxx
WEBHOOK_URL=https://stellebot.onrender.com
WEBHOOK_PATH=webhook
WEBHOOK_SECRET=unaStringaLungaECasuale
NASA_API_KEY=tuachiavenasa
```

### 4. Deploy

Clicca **Create Web Service** / **Deploy**. Nei log di Render deve comparire qualcosa come:

```text
Avvio in modalità WEBHOOK su porta 10000 → https://stellebot.onrender.com/webhook
```

Poi su Telegram: `/start`. Se il bot risponde, il webhook è vivo.

### 5. Piano Free e “spin down”

Sul piano gratuito Render spegne il processo dopo ~15 minuti senza traffico. Il primo update successivo sveglia l’istanza (anche un minuto). Per un bot 24/7 reattivo serve un piano a pagamento, oppure un ping periodico all’URL (non strettamente necessario: Telegram ritenta il webhook).

---

## Come scegliere polling o webhook

Il file `bot.py` legge l’ambiente all’avvio:

- `WEBHOOK_URL` **assente o vuoto** → `application.run_polling()` (locale)
- `WEBHOOK_URL` **impostato** → `application.run_webhook()` su `0.0.0.0:$PORT`

Non far girare polling e webhook insieme sullo stesso token: Telegram tiene un solo metodo alla volta.

Se in locale hai testato il webhook e vuoi tornare al polling, togli `WEBHOOK_URL` dal `.env` e riavvia: al prossimo `run_polling` la libreria sostituisce il webhook.

---

## Personalizzazione

In cima a `bot.py`:

```python
DEFAULT_SIGN = "libra"        # segno di /oroscopo senza argomenti
DEFAULT_LAT = 41.9028         # Roma, per Luna e pianeti
DEFAULT_LON = 12.4964
```

Cambia `DEFAULT_SIGN` in `virgo`, `scorpio`, ecc. (nome inglese minuscolo).

---

## Struttura

```text
bot.py                 # handler Telegram, polling + webhook
services/catalog.py    # pianeti, nani, stelle, costellazioni, Messier (solo id)
services/wiki.py       # Wikipedia, Wikidata, NASA Images
services/exoplanets.py # NASA Exoplanet Archive (TAP + filtri)
services/systems.py    # alberi di sistemi stellari da TAP
services/imagine.py    # mondi generati, etichettati come finti
services/skyview.py    # mappa testuale e visibilità da skymap.sh
services/spaceweather.py # Kp, flare X-ray, perigeo/apogeo
services/neo.py        # NASA NeoWs
services/eclipses.py   # Skytime eclissi
services/sheets.py     # schede e quiz da fonti live
services/progress.py   # punti quiz, missione del giorno, collezione pietre (file locale)
services/stones.py     # catalogo mineralogico, schede, laboratorio, quiz
services/runes.py      # dataset Elder Futhark
services/iss.py        # posizione ISS
services/astronomy.py  # visibilità da numeri live
ui/keyboards.py        # home a sette mondi + menu cielo + pietre
ui/texts.py            # testi home / esplora / mondi
requirements.txt
.env.example
README.md
```

Dipendenze Python: `python-telegram-bot[webhooks]`, `httpx`, `python-dotenv`.

---

## Note sulle API

- **Oroscopo**: segni in inglese (`leo`, `virgo`…). Il bot accetta anche i nomi italiani.
- **CosmyDay** è gratis e senza chiave: va indicato come fonte (il bot lo fa nei footer). Non martellare gli endpoint; c’è una cache in memoria di pochi minuti.
- **NASA `DEMO_KEY`**: limite stretto. In produzione usa una chiave tua.
- Traduzione: prima un endpoint pubblico di Google Translate, in fallback MyMemory. Se entrambi falliscono, il testo originale inglese viene comunque inviato con cornice in italiano.
