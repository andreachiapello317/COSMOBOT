# StelleBot

Bot Telegram in Python (async, `python-telegram-bot` v21+) su **oroscopo, astrologia, pianeti, stelle e astronomia**.

Il tono è chiaro, curioso e un po’ ironico: planetario tascabile, non biglietto romantico. **Oroscopi, fasi lunari, efemeridi e foto NASA arrivano da API live.** Nel codice non ci sono testi di fatti o previsioni copiati a mano.

Repository GitHub: [andreachiapello317/COSMOBOT](https://github.com/andreachiapello317/COSMOBOT)

## Cosa fa

Tutto è a **pulsanti**. Nel menu Telegram restano solo `/start` (BOTSQUAD) e `/aiuto`. Qualunque altro `/comando` viene ignorato e rimanda ai pulsanti. **📚 Aiuto** sta anche sul portale.

`/start` apre **BOTSQUAD**: un portale. **🔮 ORACOLO** ha Te stesso e Oracoli. **🔭 ASTRO** ha Cielo, Mondi, Vita, Missioni e il catalogo Pietre (l’estrazione simbolica resta in Oracoli). Ogni scheda ha una riga di presentazione. I mondi non si mescolano.

| Pulsante / mondo | Effetto | Fonte live |
| --- | --- | --- |
| 🔮 ORACOLO → Te stesso | Oroscopo (giorno / settimana / mese; senza segno usa **Bilancia**), tema natale guidato, specchio, compatibilità due segni | [freehoroscopeapi.com](https://freehoroscopeapi.com), [CosmyDay](https://cosmyday.com/api-docs) |
| 🔮 ORACOLO → Oracoli | Tarocchi, I Ching, rune, Lenormand, sì/no, pietre. Sorprendimi pesca uno strumento e dà subito la lettura | tarot API, Wilhelm 1924, dataset locali |
| 🔭 ASTRO → Cielo | Adesso, stelle, eventi, ISS, osserva da una città, Luna, APOD, asteroidi, meteore | skymap.sh, Skytime, WTIA, NASA, CosmyDay |
| 🔭 ASTRO → Mondi | Esopianeti NASA, sistemi, salvataggi, cataloghi (nani, comete, profondo) | NASA TAP + Wikipedia |
| 🔭 ASTRO → Vita | Come cerchiamo la vita, senza dichiararla | Wikipedia |
| 🔭 ASTRO → Missioni | Sonde, quiz, missione del giorno | Wikipedia + calendario locale |
| 🔭 ASTRO → Pietre | Enciclopedia, laboratorio (foto), collezione, museo | catalogo locale + Wikipedia; CLIP se `HF_TOKEN` |
| ✨ COSMICO / 🎲 casuale | Un pezzo dai mondi di ASTRO | le API già usate |

Se scrivi solo il nome di un segno (`vergine`, `Leo`, `scorpione`…) viene trattato come oroscopo.

**Tema natale** chiede data, ora e città una alla volta, geocodifica con CosmyDay e calcola Sole, Luna, Ascendente, pianeti, case e aspetti.

**Compatibilità** sta in 🔮 ORACOLO / Te stesso. Prima i due segni (Soli). Poi, se vuoi, Lune, ascendenti, Venere e Marte, Big Three. Nella Big Three, per ciascuna persona: se conosci Sole/Luna/Ascendente li scegli; altrimenti il bot li calcola da data, ora e luogo. È astrologia tradizionale, non astronomia. Niente percentuali.

**Tarocchi**: scegli lo spread (non serve una domanda). Mescola, poi gira le carte **una alla volta**. Ogni carta ha una riga sul posto e due frasi di significato. Alla fine il quadro è solo l’elenco. Una frase alle carte è opzionale.

**I Ching**: prima la domanda, poi **SONO PRONTO**, conferma, **LANCIA LE MONETE**. Le sei linee si costruiscono dal basso verso l’alto (metodo delle tre monete: 6/7/8/9). I testi arrivano dal libro Wilhelm 1924 in JSON pubblico.

**Cielo** è astronomia reale (↑ sopra, ↓ sotto, 👁 mag ≤ 6). **Oracoli** è esperienza simbolica. **Pietre** è autonomo: mineralogia da catalogo, folklore tenuto a parte. Non si mescolano.

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
services/stonephoto.py # foto lab: colore + miniature Wikipedia + CLIP opzionale
services/compat.py     # segni e sinastria (tradizione + carte live)
services/runes.py      # dataset Elder Futhark
services/iss.py        # posizione ISS
services/astronomy.py  # visibilità da numeri live
services/bots.py       # registro BOTSQUAD (ORACOLO + ASTRO)
ui/keyboards.py        # BOTSQUAD + ORACOLO + ASTRO
ui/texts.py            # testi BOTSQUAD / ORACOLO / ASTRO
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
