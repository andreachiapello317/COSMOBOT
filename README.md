# StelleBot

Bot Telegram in Python (async, `python-telegram-bot` v21+) su **oroscopo, astrologia, pianeti, stelle e astronomia**.

Il tono è chiaro, curioso e un po’ ironico: planetario tascabile, non biglietto romantico. **Oroscopi, fasi lunari, efemeridi e foto NASA arrivano da API live.** Nel codice non ci sono testi di fatti o previsioni copiati a mano.

Repository GitHub: [andreachiapello317/COSMOBOT](https://github.com/andreachiapello317/COSMOBOT)

## Cosa fa

Tutto è a **pulsanti**. Nel menu Telegram restano solo `/start` (BOTSQUAD) e `/aiuto`. Qualunque altro `/comando` viene ignorato e rimanda ai pulsanti. **📚 Aiuto** sta anche sul portale.

`/start` apre **BOTSQUAD**: un portale. **🔮 ORACOLO**, **🔭 ASTRO**, **🌍 TERRA**, **📡 OGGI**, **🧰 STRUMENTI** e **🎲 GIOCHI**. Giochi ha due porte: quiz (un mondo, un argomento) e tavolo (dadi, moneta, morra). Ogni scheda ha una riga di presentazione. I mondi non si mescolano.

| Pulsante / mondo | Effetto | Fonte live |
| --- | --- | --- |
| 🔮 ORACOLO → Te stesso | Oroscopo (giorno / settimana / mese; senza segno usa **Bilancia**), tema natale guidato, specchio, compatibilità due segni | [freehoroscopeapi.com](https://freehoroscopeapi.com), [CosmyDay](https://cosmyday.com/api-docs) |
| 🔮 ORACOLO → Consultazioni | Tarocchi, I Ching, rune, Lenormand, sì/no, pietra del giorno. «Fai scegliere all'oracolo» pesca uno strumento e dà subito la lettura | tarot API, Wilhelm 1924, dataset locali |
| 🔮 ORACOLO → Interroga il cielo | Città (default **Cuneo**), poi legge luna, stelle e pianeti sopra di te. Niente carte | skymap + sunrisesunset; il testo è folklore |
| 🔭 ASTRO → Cielo | Città (default **Cuneo**); Luna, alba/tramonto, Terra, schema emoji Sole–Luna–Terra | sunrisesunset + Astronomy Engine |
| 🔭 ASTRO → Meteo | Subito il meteo di **Cuneo** (o dell'ultima città), oggi e domani. Puoi cambiare giorni o città | [Open-Meteo](https://open-meteo.com) |
| 🔭 ASTRO → Osservatorio | Cielo di adesso (6 carte + grado), Horizons NASA, Satelliti (posizioni, equipaggio, Worldview/GIBS: vero, falso, notti, fuochi) | Hipparcos + Astronomy Engine + [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/) + WTIA + TLE/SGP4 + [NASA Worldview / GIBS](https://wvs.earthdata.nasa.gov) |
| 🔭 ASTRO → Studia lo spazio | Enciclopedia Wikipedia: sistema solare, stelle, galassie, satelliti, sonde, missioni. Niente salvati né casuale | Wikipedia / Wikidata / NASA TAP |
| 🧰 STRUMENTI → Calcolatrice | Scientifica: sen, log, radici, π, gradi/radianti | calcolo locale |
| 🧰 STRUMENTI → Conversioni | Lunghezza, massa, temperatura, velocità, volume, angoli, cielo, tempo | calcolo locale |
| 🧰 STRUMENTI → Bussola | Posizione, coordinate, nord, verso un luogo. Via e numero o numeri scritti | Open-Meteo + BGS WMM + Nominatim |
| 🧰 STRUMENTI → Calendario | Ora e mese; eventi per regioni / religiose / mondo (amori, buffe…); compleanni | orologio + computus + file locale |
| 🎲 GIOCHI → Quiz | Una prova per ogni bot: oracolo, astro, terra, oggi, strumenti | cataloghi locali; ASTRO ha anche Wikipedia live |
| 🎲 GIOCHI → Tavolo | Dadi (1d6, 2d6, 3d6, d20), moneta, morra, indovina 1–20, alto o basso | caso locale; non è un oracolo e non si vince soldi |
| 📡 OGGI → Mercati | Valute BCE, crypto, indici, materie. Cerca un nome del catalogo | [Frankfurter/ECB](https://www.frankfurter.app) + [CoinGecko](https://www.coingecko.com) + [Yahoo chart](https://finance.yahoo.com) + [gold-api](https://api.gold-api.com) |
| 📡 OGGI → Notizie | Italia, mondo, economia, tecnologia, rassegna. 5 titoli a pagina, link alla fonte | RSS [ANSA](https://www.ansa.it) + [Google News IT](https://news.google.com) |
| 🌍 TERRA → Eventi | Sulla città: solo i tasti delle categorie con eventi (500 km, 7 giorni). Mondo + cataloghi restano. Foto Worldview/GIBS | [USGS](https://earthquake.usgs.gov) + [NASA EONET](https://eonet.gsfc.nasa.gov) + [FIRMS](https://firms.modaps.eosdis.nasa.gov) + [GIBS](https://wvs.earthdata.nasa.gov) |
| 🌍 TERRA → Eventi → categorie | Terremoti USGS; incendi FIRMS+EONET; tempeste, vulcani, alluvioni, frane, polvere EONET (compaiono solo se ci sono); satellite GIBS | USGS + EONET + FIRMS + GIBS |
| 🌍 TERRA → Eventi → Cataloghi | Feed lunghi aperti (USGS / EONET) | USGS + EONET |
| 🌍 TERRA → Fauna | Osservati recenti (iNat/GBIF/eBird intorno al luogo), fauna nel mondo | [iNaturalist](https://www.inaturalist.org) + [GBIF](https://www.gbif.org) + [eBird](https://ebird.org) (se `EBIRD_API_KEY`) |
| 🌍 TERRA → Pietre | Esplora (filtri del catalogo + geologia del luogo), cerca, laboratorio (foto). Niente giorno/casuale/giochi/collezione | catalogo locale + Wikipedia + [Macrostrat](https://macrostrat.org); CLIP se `HF_TOKEN` |

Se scrivi solo il nome di un segno (`vergine`, `Leo`, `scorpione`…) viene trattato come oroscopo.

**Tema natale** chiede data, ora e città una alla volta, geocodifica con CosmyDay e calcola Sole, Luna, Ascendente, pianeti, case e aspetti.

**Compatibilità** sta in 🔮 ORACOLO / Te stesso. Prima i due segni (Soli). Poi, se vuoi, Lune, ascendenti, Venere e Marte, Big Three. Nella Big Three, per ciascuna persona: se conosci Sole/Luna/Ascendente li scegli; altrimenti il bot li calcola da data, ora e luogo. È astrologia tradizionale, non astronomia. Niente percentuali.

**Tarocchi**: scegli lo spread (non serve una domanda). Mescola, poi gira le carte **una alla volta**. Ogni carta ha una riga sul posto e due frasi di significato. Alla fine il quadro elenca le uscite e **interpreta** cosa dicono insieme. Una frase alle carte è opzionale.

**I Ching**: domanda, monete, poi **Ora / Si muove / Verso / In pratica**. Wilhelm 1924, tradotto a pezzi corti, non un muro di testo.

**Rune** e **Lenormand**: come i tarocchi — mescola, gira una alla volta, quadro finale con interpretazione. La domanda è facoltativa.

**Pietre in Consultazioni**: una sola scheda, la **pietra del giorno**. Si può chiedere quante volte si vuole: fino a mezzanotte (Roma) è sempre la stessa. Formula, proprietà, curiosità, link Wikipedia e un oracolo folklorico (se «porta bene o male»). Non è mineralogia.

**Cielo** in ASTRO è Sole, Luna e Terra da un luogo: scheda alba/tramonto, Luna (fase, illuminazione, quarti), Terra (giorno/notte, stagione, distanze) e uno **schema a emoji** Sole–Luna–Terra. Non è l'enciclopedia di TERRA. **Osservatorio** ha un solo **Cielo di adesso**: le 6 carte PNG (frecce per lo stile e per il grado: Tutto / Facile / Occhio nudo / Binocolo) e, a parte, **Cosa osservare stasera**. **Tutto** è il cielo completo, senza filtro. Gli altri gradi nascondono Sole e oggetti troppo deboli o bassi; se è ancora giorno usano le 22:00. **Horizons NASA** resta a parte (schede singolo corpo da [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/tutorial.html); **Calcoli**: più alto, più luminoso, separazioni, prossimo a sorgere; stelle Hipparcos; eventi e prossimi). Horizons non è un catalogo stellare. **Cosa osservare stasera** pesca le stelle con nome proprio dal catalogo Hipparcos in crescendo: Facile ⊂ Occhio nudo ⊂ Binocolo (le stelle facili restano anche nei gradi dopo; niente Tutto). Ogni grado ha la sua mappa PNG. **Satelliti** in Osservatorio ha tre porte: **Posizione satelliti** (ISS, Tiangong, Hubble, stazioni, Starlink), **Chi è lassù**, **Osservazione Terra**. La foto Terra è [NASA Worldview / GIBS](https://worldview.earthdata.nasa.gov): VIIRS o MODIS Terra a colori veri, falso colore 7-2-1, luci notturne, anomalie termiche (fuochi). Luogo e zoom (città / zona / regione) restano solo in quella cartella: cambiarli cambia l'immagine, non Cielo né Starlink. I passaggi sopra una città non si inventano. **Studia lo spazio** è l'enciclopedia, anche satelliti e sonde. **Meteo** apre subito la previsione di Cuneo (o dell'ultima città): oggi e domani, con i tasti per 3/7/14 giorni o un'altra città. **STRUMENTI** unisce calcolatrice scientifica, conversioni, bussola (con le coordinate), eventi di calendario (Pasqua, Natale, Italia, mondo, stagioni) e ora+calendario italiano. Il calendario non ha cambio città. **GIOCHI** è il sesto bot: Quiz (una porta per ogni mondo) e Tavolo (dadi, moneta, morra, indovina). Non è un oracolo. **Interroga il cielo** in ORACOLO usa la mappa come specchio mistico. **Consultazioni** è carte e strumenti. **🌍 TERRA** ha Eventi e calamità (terremoti USGS, incendi FIRMS+EONET, altri fenomeni EONET, foto NASA Worldview/GIBS sul punto), Fauna (osservati iNat/GBIF/eBird intorno al luogo) e Pietre (catalogo, laboratorio, geologia Macrostrat sul punto). **📡 OGGI** ha Mercati (Frankfurter/BCE, CoinGecko, Yahoo chart, gold-api) e Notizie (RSS ANSA e Google News Italia). Niente consigli di investimento. Se non scegli una città, il bot usa **Cuneo, Italia**. Il tasto GPS è stato tolto: su Telegram desktop non funzionava. Non si mescolano.

Nel laboratorio pietre (pietra al centro, tavolo uniforme) il bot legge il colore, confronta le miniature Wikipedia e, se c’è `HF_TOKEN`, prova CLIP. Cinque ipotesi, non un’analisi mineralogica. Niente prezzi inventati.

Su ogni schermata (tranne la home) c’è **⬅️ Indietro**: torna al menu precedente. **🏠 Inizio** è sempre BOTSQUAD.

In chat il bot tiene **un solo messaggio**: ogni pulsante modifica (o sostituisce) la risposta precedente. Se scrivi `/start` o un testo, il messaggio utente viene cancellato appena la risposta è pronta.

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

Opzionale per il laboratorio pietre: un token Hugging Face. Senza, il bot confronta comunque la foto con le miniature Wikipedia del catalogo (stesso colore). Con `HF_TOKEN` prova anche CLIP zero-shot.

```env
HF_TOKEN=hf_...
```

Opzionale per gli incendi: una `MAP_KEY` FIRMS (gratis). Senza, il bot usa i CSV pubblici VIIRS 24h per area.

```env
FIRMS_MAP_KEY=
```

Opzionale: chiave eBird. Senza, gli uccelli restano dentro Osservati recenti via GBIF.

```env
EBIRD_API_KEY=
```

Avvio:

```bash
python bot.py
```

Nei log deve comparire `Avvio in modalità POLLING`. Apri Telegram, cerca il bot, manda `/start` e usa i pulsanti (ORACOLO, ASTRO, Aiuto). Nel menu comandi di Telegram restano solo Start e Aiuto.

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
DEFAULT_SIGN = "libra"        # segno di default dell'oroscopo
DEFAULT_LAT = 44.3904         # Cuneo, Italia
DEFAULT_LON = 7.5483
DEFAULT_PLACE_NAME = "Cuneo, Italia"
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
services/horizons.py   # JPL Horizons observer: pianeti, luna, comete, asteroidi
services/moon.py       # fasi e quarti lunari (Astronomy Engine)
services/skycatalog.py # Hipparcos mag ≤ 5.2 e figure IAU (non Horizons)
services/skychart.py   # PNG del cielo di adesso
services/watchevents.py # stasera e prossimi eventi calcolati
services/spaceweather.py # Kp, flare X-ray, perigeo/apogeo
services/neo.py        # NASA NeoWs
services/eclipses.py   # Skytime eclissi
services/sheets.py     # schede e quiz da fonti live
services/progress.py   # punti quiz, missione del giorno, collezione pietre (file locale)
services/stones.py     # catalogo mineralogico, schede, laboratorio, filtri Esplora
services/stonephoto.py # foto lab: colore + miniature Wikipedia + CLIP opzionale
services/compat.py     # segni e sinastria (tradizione + carte live)
services/runes.py      # dataset Elder Futhark
services/iss.py        # posizione ISS e equipaggio
services/sats.py       # TLE live + SGP4 (Tiangong, Hubble, Terra, Starlink)
services/satimages.py  # NASA Worldview / GIBS: vero, falso, notti, fuochi + zoom
services/astronomy.py  # visibilità da numeri live
services/oggi.py       # mercati live + RSS notizie (bot OGGI)
services/games.py      # dadi, moneta, morra, indovina (bot GIOCHI)
services/bots.py       # registro BOTSQUAD (sei bot)
services/tools.py      # coordinate, ora e calendario civile di STRUMENTI
services/calevents.py  # Pasqua, Natale, feste civili, stagioni
services/birthdays.py  # compleanni nel calendario + avviso del giorno
services/wildlife.py   # Fauna: osservati recenti iNat/GBIF/eBird; fauna nel mondo
services/calamity.py   # Eventi & calamità: USGS + EONET + FIRMS + GIBS
ui/keyboards.py        # BOTSQUAD + ORACOLO + ASTRO + STRUMENTI
ui/texts.py            # testi BOTSQUAD / ORACOLO / ASTRO / STRUMENTI
requirements.txt
.env.example
README.md
```

Dipendenze Python: `python-telegram-bot[webhooks]`, `httpx`, `python-dotenv`, `Pillow`.

---

## Note sulle API

- **Oroscopo**: segni in inglese (`leo`, `virgo`…). Il bot accetta anche i nomi italiani.
- **CosmyDay** è gratis e senza chiave: va indicato come fonte (il bot lo fa nei footer). Non martellare gli endpoint; c’è una cache in memoria di pochi minuti.
- **NASA `DEMO_KEY`**: limite stretto. In produzione usa una chiave tua.
- Traduzione: prima un endpoint pubblico di Google Translate, in fallback MyMemory. Se entrambi falliscono, il testo originale inglese viene comunque inviato con cornice in italiano.
- **Foto pietre**: il bot isola la pietra (angoli = sfondo, meno peso a mani/tavolo) e usa quel colore come vincolo. Poi confronta le miniature Wikipedia (`data/stone_refs.json`). `HF_TOKEN` abilita CLIP; senza token resta Wikipedia. Non è un’analisi di laboratorio.
