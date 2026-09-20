"""Testi di interfaccia: BOTSQUAD, ORACOLO e ASTRO. I mondi non si mescolano."""

import html as _html


def _card(title: str, intro: str, body: str = "") -> str:
    """Scheda: titolo + presentazione minima + eventuale corpo."""
    text = f"{title}\n<i>{intro}</i>"
    extra = body.strip()
    if extra:
        text = f"{text}\n\n{extra}"
    return text


def all_hub_text() -> str:
    return _card(
        "🪐 <b>BOTSQUAD</b>",
        "Quattro bot in un solo Telegram. Ognuno ha i suoi mondi, e non si mescolano.",
        "🔮 <b>ORACOLO</b> — te stesso, consultazioni, interroga il cielo.\n"
        "🔭 <b>ASTRO</b> — osservatorio: cielo, meteo, mondi.\n"
        "🌍 <b>GEO</b> — la Terra: pietre, terremoti, vulcani, oceani.\n"
        "🧮 <b>CALC</b> — calcolatrice a pulsanti.\n\n"
        "Tutto a pulsanti. 📚 Aiuto spiega i mondi. 🏠 Inizio torna sempre qui.",
    )


def home_text() -> str:
    return all_hub_text()


def oracolo_hub_text() -> str:
    return _card(
        "🔮 <b>ORACOLO</b>",
        "Bot di BOTSQUAD per guardarsi dentro. Simboli, non telescopio.",
        "🔮 <b>TE STESSO</b> — oroscopo, tema natale, specchio, compatibilità\n"
        "🃏 <b>CONSULTAZIONI</b> — tarocchi, I Ching, rune, Lenormand, sì/no, pietre\n"
        "🌌 <b>INTERROGA IL CIELO</b> — luna, stelle e pianeti sopra la tua città\n\n"
        "Il cielo misurato sta in 🔭 ASTRO. Le pietre e la Terra stanno in 🌍 GEO.",
    )


def astro_hub_text() -> str:
    return _card(
        "🔭 <b>ASTRO</b>",
        "Osservatorio stellare di BOTSQUAD. Numeri live, cataloghi, niente divinazione.",
        "🔭 <b>CIELO</b> — prima la città, poi luna, stelle, alba, tramonto, eventi\n"
        "🌤️ <b>METEO</b> — scegli città e giorni (se non dici nulla: oggi e domani)\n"
        "🪐 <b>MONDI</b> — esopianeti, pianeti, vita, missioni\n\n"
        "Le pietre e i dati sulla Terra stanno in 🌍 GEO."
    )


def cosmo_hub_text() -> str:
    return oracolo_hub_text()


def esplora_text() -> str:
    return all_hub_text()


def next_bot_text() -> str:
    return astro_hub_text()


def domanda_text() -> str:
    return lettura_text()


def lettura_text() -> str:
    return _card(
        "📖 <b>LETTURA</b>",
        "Una situazione, uno strumento. È uno specchio, non un verdetto.",
        "Scrivi cosa sta succedendo — una frase basta.\n"
        "Poi scegli, o lascia che lo scelga ORACOLO.\n\n"
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n"
        "🔮 Fai scegliere all'oracolo — pesco io il metodo.",
    )


def oracoli_text() -> str:
    return _card(
        "🃏 <b>CONSULTAZIONI</b>",
        "Sei strumenti, tutti simbolici. Nessun verdetto, nessuna astronomia.",
        "🃏 <b>Tarocchi</b> — mazzo live, spread a scelta\n"
        "☯️ <b>I Ching</b> — sei lanci, libro Wilhelm\n"
        "🪶 <b>Rune</b> — Elder Futhark, 1 o 3\n"
        "🌿 <b>Lenormand</b> — 36 sibille, 1/3/5/9\n"
        "🪞 <b>Sì / No</b> — un'inclinazione, non un verdetto\n"
        "💎 <b>Pietre</b> — pietra del giorno, fino a mezzanotte\n\n"
        "🔮 <b>Fai scegliere all'oracolo</b> — pesco uno strumento e ti do subito la lettura.",
    )


def rune_intro_text() -> str:
    return _card(
        "🪶 <b>RUNE</b>",
        "Ventiquattro segni dell'Elder Futhark. Una o tre, una alla volta. Non serve una domanda.",
        "ᚠ Una — il clima di adesso.\n"
        "ᛏ Tre — situazione, ostacolo, direzione.",
    )


def world_self_text() -> str:
    return _card(
        "🔮 <b>TE STESSO</b>",
        "Oroscopo, carta natale, specchio e compatibilità. Tradizione, non astronomia.",
        "🌌 Tema · 🔮 Oroscopo · 🪞 Specchio · ❤️ Compatibilità",
    )


def compat_hub_text(*, has_natal: bool = False, has_syn: bool = False) -> str:
    return _card(
        "❤️ <b>COMPATIBILITÀ</b>",
        "Due persone, un confronto. Nessuna percentuale, nessuna previsione.",
        "♈ <b>Due segni</b> — i due Soli, il confronto classico.\n"
        "✨ <b>Avanzate</b> — Lune, ascendenti, Venere e Marte, Big Three.\n\n"
        "Nella Big Three, per ciascuna persona: se li sai li scegli, "
        "altrimenti li calcolo da data, ora e luogo.",
    )


def compat_advanced_text(*, has_natal: bool = False, has_syn: bool = False) -> str:
    overlay = "🏠 Overlay delle case: dopo due carte calcolate.\n" if has_syn else ""
    return _card(
        "✨ <b>CONFRONTI AVANZATI</b>",
        "Un altro punto della carta, o le tre porte insieme.",
        "🌙 <b>Lune</b> — come vi sentite e vi accudite.\n"
        "⬆️ <b>Ascendenti</b> — come vi incontrate.\n"
        "♀️♂️ <b>Venere e Marte</b> — gusto e slancio.\n"
        "☀️🌙⬆️ <b>Big Three</b> — per ognuno: li sai già o li calcolo dalla nascita.\n"
        f"{overlay}\n"
        "Tradizione, non un test di coppia.",
    )


def world_div_text() -> str:
    return oracoli_text()


def world_asksky_text() -> str:
    return _card(
        "🌌 <b>INTERROGA IL CIELO</b>",
        "Prima la città. Poi il cielo sopra di te: luna, stelle, pianeti. Niente carte.",
        "Altezza e orari sono astronomia. La lettura è mistica, non un effetto dimostrato.",
    )


def world_sky_text(place: str = "") -> str:
    where = (
        f"Città salvata: <b>{_html.escape(place)}</b>."
        if place
        else "Appena entri, chiedo la città e la tengo."
    )
    return _card(
        "🔭 <b>CIELO</b>",
        "Osservatorio: luna, stelle, alba, tramonto, eventi. Numeri live, niente enciclopedia e niente oracoli.",
        f"{where}\n"
        "Ogni pulsante usa quella città. In fondo: 📍 Cambia città.\n\n"
        "Il meteo ha la sua sezione. Pianeti, vita e missioni stanno in 🪐 Mondi.",
    )


def meteo_span_text(place: str) -> str:
    return _card(
        f"🌤️ <b>METEO — {_html.escape(place)}</b>",
        "Quanti giorni, o quali. Se non dici nulla: oggi e domani.",
        "Tocca una finestra, oppure scrivi: <code>3 giorni</code>, "
        "<code>lunedì</code>, <code>da venerdì a domenica</code>.",
    )


def calc_hub_text(expr: str = "", error: str = "") -> str:
    shown = expr.strip() if expr and expr.strip() else "0"
    extra = f"\n\n⚠️ {_html.escape(error)}" if error else ""
    return (
        "🧮 <b>CALC</b>\n"
        "<i>Calcolatrice a pulsanti. Solo numeri, niente cielo e niente oracoli.</i>\n\n"
        f"<code>{_html.escape(shown)}</code>"
        f"{extra}"
    )


def world_mondi_text() -> str:
    return _card(
        "🪐 <b>MONDI</b>",
        "Un esploratore NASA e Wikipedia. Non un oracolo.",
        "🌍 Filtri · ⭐ Sistemi · ☀️ Sistema Solare\n"
        "🪐 Pianeti · 🌑 Lune · 🪨 Asteroidi · 📌 Salvati\n"
        "👽 Vita · 🚀 Missioni\n\n"
        "Oceanici e abitabili = modelli, non oceani e non vita.",
    )


def mondi_hub_text() -> str:
    return _card(
        "🌌 <b>ESPLORA I MONDI</b>",
        "Ogni filtro è una ricerca sull'archivio, o una voce Wikipedia.",
        "🌊 Oceanici e 🌱 abitabili = raggio e temperatura, non oceani e non vita.\n"
        "🌋 Vulcanici, 💍 anelli, 🌙 molte lune: corpi del Sistema Solare con voce.\n"
        "🎲 Genera = mondo immaginario, scritto grande che è finto.",
    )


def cosmo_text() -> str:
    return _card(
        "🌌 <b>COSMO</b>",
        "Mappa dell'universo osservabile. Solo cataloghi, niente carte.",
        "⭐ Stelle · 🪐 Sistemi · 🌍 Mondi\n"
        "🌌 Galassie · 🌀 Nebulose · 🕳️ Buchi neri\n"
        "💥 Supernovae · 🔭 Cielo profondo",
    )


def sistemi_text() -> str:
    return _card(
        "⭐ <b>SISTEMI STELLARI</b>",
        "Una stella ospite e i suoi pianeti, ad albero.",
        "Niente lune extrasolari: l'archivio quasi non le ha.\n"
        "Il Sistema Solare resta la scheda Wikidata, non uno scarico JPL.",
    )


def life_plus_text() -> str:
    return _card(
        "🧬 <b>E SE CI FOSSE VITA?</b>",
        "Due piani tenuti distinti: documentato, e speculazione.",
        "<b>Osservato</b> — SETI, firme biologiche, estremofili, oceani sotto il ghiaccio.\n\n"
        "<b>Speculazione</b> — Fermi è un argomento, non una rivelazione. "
        "I candidati HZ sono un filtro numerico.",
    )


def world_vita_text() -> str:
    return _card(
        "👽 <b>VITA</b>",
        "Come la cerchiamo. Nessun mondo dichiarato abitato.",
        "Oceani sotto il ghiaccio, esopianeti, SETI, biosignature.\n"
        "La zona abitabile è un modello di temperatura e raggio.",
    )


def geo_hub_text() -> str:
    return _card(
        "🌍 <b>GEO</b>",
        "Bot di BOTSQUAD per la Terra. Misure e cataloghi, niente oracoli.",
        "🌍 <b>TERRA</b> — crosta, mantello, nucleo, atmosfera\n"
        "💎 <b>PIETRE</b> — mineralogia, laboratorio, collezione\n"
        "🌋 <b>TERREMOTI</b> — feed USGS live\n"
        "🔥 <b>VULCANI</b> — schede Wikipedia\n"
        "🌊 <b>ACQUA</b> — oceani, fosse, ciclo idrologico\n"
        "🧭 <b>PLACCHE</b> — tettonica\n"
        "🌪️ <b>EVENTI</b> — NASA EONET",
    )


def world_terra_text() -> str:
    return _card(
        "🌍 <b>TERRA</b>",
        "Il pianeta sotto i piedi. Voci Wikipedia e misure Wikidata.",
        "Crosta, mantello, nucleo, campo magnetico, atmosfera, tettonica.\n"
        "Niente geologia inventata: apro la voce, non la riscrivo.",
    )


def world_quake_text() -> str:
    return _card(
        "🌋 <b>TERREMOTI</b>",
        "Catalogo USGS, non un allarme. Scegli il feed.",
        "📅 24 ore, magnitudo ≥ 4,5\n"
        "📆 7 giorni, magnitudo ≥ 2,5\n"
        "⚠️ Solo gli eventi che USGS marca come significativi",
    )


def world_volc_text() -> str:
    return _card(
        "🔥 <b>VULCANI</b>",
        "Schede di vulcani noti. Wikipedia, non un bollettino eruttivo.",
        "Tocca un nome. Per gli eventi aperti in questo momento: 🌪️ Eventi Terra.",
    )


def world_water_text() -> str:
    return _card(
        "🌊 <b>ACQUA</b>",
        "Oceani, fosse, correnti, ciclo dell'acqua. Voci, non un atlante inventato.",
        "Pacifico, Atlantico, Indiano, Mediterraneo, polarità, Fossa delle Marianne.",
    )


def world_plates_text() -> str:
    return _card(
        "🧭 <b>PLACCHE</b>",
        "Le placche tettoniche principali. Wikipedia / Wikidata.",
        "Pacifica, nordamericana, eurasiatica, africana, sudamericana, e le altre.",
    )


def world_pietre_text() -> str:
    return pietre_hub_text()


def pietre_hub_text() -> str:
    return _card(
        "💎 <b>PIETRE</b>",
        "Mineralogia da catalogo, nel bot GEO. Il folklore sta in ORACOLO, a parte.",
        "Foto: pietra al centro, tavolo uniforme. Non è un'analisi.\n\n"
        "🧭 Esplora · 🔬 Laboratorio · 🎒 Collezione · 🧠 Giochi",
    )


def world_miss_text() -> str:
    return _card(
        "🚀 <b>MISSIONI</b>",
        "Voli veri, sonde, lezioni e una sfida al giorno.",
        "Schede delle missioni, astronauti, quiz a quattro livelli.",
    )
