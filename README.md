# StelleBot

Bot Telegram in Python (async, `python-telegram-bot` v21+) su **oroscopo, astrologia, pianeti, stelle e astronomia**.

Il tono è chiaro, curioso e un po’ ironico: planetario tascabile, non biglietto romantico. **Oroscopi, fasi lunari, efemeridi e foto NASA arrivano da API live.** Nel codice non ci sono testi di fatti o previsioni copiati a mano.

Repository GitHub: [andreachiapello317/COSMOBOT](https://github.com/andreachiapello317/COSMOBOT)

## Cosa fa

| Comando | Effetto | Fonte live |
| --- | --- | --- |
| `/start` | Presenta il bot e i comandi | — |
| `/oroscopo [segno]` | Oroscopo del giorno. Senza segno usa **Leone** (`DEFAULT_SIGN` in `bot.py`) | [freehoroscopeapi.com](https://freehoroscopeapi.com) |
| `/luna` | Fase, illuminazione, moonrise/moonset + spiegazione del giorno | [sunrisesunset.io](https://sunrisesunset.io/api/) + [CosmyDay](https://api.cosmyday.com/content/moon) |
| `/pianeti` | Posizioni attuali dei pianeti principali sopra Roma | [CosmyDay `/natal`](https://cosmyday.com/api-docs) (Swiss Ephemeris) |
| `/apod` | Astronomy Picture of the Day (foto o video) | [NASA APOD](https://api.nasa.gov) |
| `/stelle` | Una scheda NASA pescata a caso (`count=1`) | NASA APOD random |
| `/aiuto` | Elenco comandi | — |

Se scrivi solo il nome di un segno (`vergine`, `Leo`, `scorpione`…) viene trattato come `/oroscopo`.

In chat il bot tiene **un solo messaggio**: ogni comando modifica (o sostituisce) la risposta precedente, senza accodarne di nuove.

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
DEFAULT_SIGN = "leo"          # segno di /oroscopo senza argomenti
DEFAULT_LAT = 41.9028         # Roma, per Luna e pianeti
DEFAULT_LON = 12.4964
```

Cambia `DEFAULT_SIGN` in `virgo`, `scorpio`, ecc. (nome inglese minuscolo).

---

## Struttura

```text
bot.py           # applicazione completa
requirements.txt
.env.example     # modello, da copiare in .env (mai committare il token)
README.md
```

Dipendenze Python: `python-telegram-bot[webhooks]`, `httpx`, `python-dotenv`.

---

## Note sulle API

- **Oroscopo**: segni in inglese (`leo`, `virgo`…). Il bot accetta anche i nomi italiani.
- **CosmyDay** è gratis e senza chiave: va indicato come fonte (il bot lo fa nei footer). Non martellare gli endpoint; c’è una cache in memoria di pochi minuti.
- **NASA `DEMO_KEY`**: limite stretto. In produzione usa una chiave tua.
- Traduzione: prima un endpoint pubblico di Google Translate, in fallback MyMemory. Se entrambi falliscono, il testo originale inglese viene comunque inviato con cornice in italiano.
