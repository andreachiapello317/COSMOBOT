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
        "Cinque bot in un solo Telegram. Ognuno ha i suoi mondi, e non si mescolano.",
        "🔮 <b>ORACOLO</b> — te stesso, consultazioni, interroga il cielo.\n"
        "🔭 <b>ASTRO</b> — osservatorio: cielo, meteo, mondi.\n"
        "🌿 <b>NATURA</b> — flora, fauna, pietre.\n"
        "🧰 <b>STRUMENTI</b> — calcolatrice, bussola, coordinate, tempo.\n"
        "🧩 <b>QUIZ</b> — una prova per ogni bot.\n\n"
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
        "🌌 <b>INTERROGA IL CIELO</b> — luna, stelle e pianeti sopra di te (città, default Cuneo)\n\n"
        "Il cielo misurato sta in 🔭 ASTRO. La Terra e le pietre stanno in 🌿 NATURA.",
    )


def astro_hub_text() -> str:
    return _card(
        "🔭 <b>ASTRO</b>",
        "Osservatorio stellare di BOTSQUAD. Numeri live, cataloghi, niente divinazione.",
        "☀️ <b>CIELO</b> — luna, sole, terra e uno schema a emoji\n"
        "🌤️ <b>METEO</b> — Cuneo (o l'ultima città), oggi e domani; puoi cambiare giorni\n"
        "🔭 <b>OSSERVATORIO</b> — cielo di adesso (visibilità sulla carta), Horizons NASA, satelliti live\n"
        "🚀 <b>STUDIA LO SPAZIO</b> — enciclopedia Wikipedia, anche i satelliti\n\n"
        "La Terra e le pietre stanno in 🌿 NATURA."
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
        "Prima il luogo (default Cuneo). Poi il cielo sopra di te: luna, stelle, pianeti. Niente carte.",
        "Altezza e orari sono astronomia. La lettura è mistica, non un effetto dimostrato.",
    )


def world_sky_text(place: str = "") -> str:
    where = (
        f"Città salvata: <b>{_html.escape(place)}</b>."
        if place
        else "Se non scegli una città, uso Cuneo."
    )
    return _card(
        "☀️ <b>CIELO</b>",
        "Sole, Luna e Terra da questo luogo. Niente stelle, niente eventi, niente enciclopedia.",
        f"{where}\n"
        "🌙 Luna · 🌅 Alba e tramonto · 🌍 Terra · ☀️🌙🌍 schema a emoji.\n"
        "Stelle, eventi e carte PNG stanno in 🔭 Osservatorio.",
    )


def world_watch_text(place: str = "") -> str:
    where = (
        f"Città salvata: <b>{_html.escape(place)}</b>."
        if place
        else "Se non scegli una città, uso Cuneo."
    )
    return _card(
        "🔭 <b>OSSERVATORIO</b>",
        "Cosa sta sopra di te, adesso. Stelle da Hipparcos; Sole, Luna, pianeti e comete da JPL Horizons.",
        f"{where}\n"
        "🔭 Cielo di adesso — 6 carte con grado sulla cartina, e cosa osservare stasera\n"
        "📡 Horizons NASA — stelle, luna, pianeti, comete, calcoli, eventi\n"
        "🛰️ Satelliti — ISS, equipaggio, Tiangong, Hubble, Terra, meteo\n\n"
        "Horizons non è un catalogo di stelle. L'enciclopedia sta in Studia lo spazio.",
    )


def watch_horizons_text(place: str = "") -> str:
    where = (
        f"Città salvata: <b>{_html.escape(place)}</b>."
        if place
        else "Se non scegli una città, uso Cuneo."
    )
    return _card(
        "📡 <b>HORIZONS NASA</b>",
        "Cosa sta sopra di te, in italiano. I numeri arrivano da JPL Horizons e Hipparcos.",
        f"{where}\n"
        "⭐ <b>STELLE</b> — le più luminose sopra\n"
        "🪐 <b>PIANETI</b> / 🌙 <b>LUNA</b> / ☄️ <b>COMETE</b> — scheda del singolo corpo\n"
        "📐 <b>CALCOLI</b> — confronti: più alto, più luminoso, separazioni, prossimo a sorgere\n"
        "🌠 <b>EVENTI</b> · 📅 <b>PROSSIMI</b>\n\n"
        "Le schede sono JPL Horizons. I calcoli (angoli e orari) sono Astronomy Engine, dallo stesso luogo. "
        "Non è un catalogo di satelliti.",
    )


def watch_eye_hub_text(place: str = "", level: str = "full") -> str:
    return watch_sky_pick_text(place, level)


def watch_sky_pick_text(place: str = "", level: str = "full") -> str:
    from services.skychart import eye_is_full, eye_level

    where = _html.escape(place) if place else "Cuneo"
    cfg = eye_level(level)
    if eye_is_full(level):
        grade = (
            f"Grado adesso: <b>{cfg['emoji']} {cfg['it']}</b> — "
            "tutti gli oggetti sopra l'orizzonte."
        )
    else:
        grade = (
            f"Grado adesso: <b>{cfg['emoji']} {cfg['it']}</b> — "
            f"stelle mag ≤ {cfg['star']:.1f}, pianeti mag ≤ {cfg['planet']:.1f}, "
            f"altezza ≥ {cfg['alt']:.0f}°."
        )
    return _card(
        f"🔭 <b>CIELO DI ADESSO — {where.upper()}</b>",
        "Due porte. Sulla carta scorri stile e grado con le frecce.",
        f"{grade}\n\n"
        "🗺️ <b>PROFESSIONALE</b> — sei carte PNG: classica, figure, atlante, polare, eclittica, sfera. "
        "Frecce sopra per il disegno, frecce sotto per il grado.\n"
        "🔭 <b>COSA OSSERVARE STASERA</b> — elenco e mappa solo di quegli oggetti, a parte\n\n"
        "🌌 Tutto · ✨ Facile · 👁️ Occhio nudo · 🔭 Binocolo. "
        "Tutto è il cielo completo. Se non è Tutto e c'è ancora il Sole, uso le 22:00.",
    )


def meteo_span_text(place: str) -> str:
    return _card(
        f"🌤️ <b>METEO — {_html.escape(place)}</b>",
        "Quanti giorni, o quali. Se non dici nulla: oggi e domani.",
        "Tocca una finestra, oppure scrivi: <code>3 giorni</code>, "
        "<code>lunedì</code>, <code>da venerdì a domenica</code>.",
    )


def math_hub_text() -> str:
    return tool_hub_text()


def tool_hub_text() -> str:
    return _card(
        "🧰 <b>STRUMENTI</b>",
        "Attrezzi. Numeri veri, niente oracoli e niente enciclopedia.",
        "🧮 <b>CALCOLATRICE</b> — tasti, come sul telefono\n"
        "➗ <b>PERCENTUALE</b> · 🔄 <b>CONVERSIONI</b>\n"
        "🧭 <b>BUSSOLA</b> — posizione, nord, verso un luogo\n"
        "📐 <b>COORDINATE</b> — decimale e gradi-minuti-secondi\n"
        "📅 <b>GIORNO GIULIANO</b> — JD / MJD da Astronomy Engine\n"
        "🕐 <b>CHE ORA È</b> — ora locale di una città (Open-Meteo)",
    )


def calc_hub_text(expr: str = "", error: str = "") -> str:
    shown = expr.strip() if expr and expr.strip() else "0"
    extra = f"\n\n⚠️ {_html.escape(error)}" if error else ""
    return (
        "🧮 <b>CALCOLATRICE</b>\n"
        "<i>Una funzione di STRUMENTI. Solo aritmetica.</i>\n\n"
        f"<code>{_html.escape(shown)}</code>"
        f"{extra}"
    )


def math_percent_text(result: str = "") -> str:
    extra = f"\n\nRisultato: <b>{_html.escape(result)}</b>" if result else ""
    return _card(
        "➗ <b>PERCENTUALE</b>",
        "Tocca un esempio, oppure scrivi: 20% di 150 · 15 su 60 · aumenta 80 del 10% · sconta 80 del 10%.",
        extra,
    )


def math_convert_text(kind: str = "", result: str = "") -> str:
    wait = (
        f"Scrivi il numero da convertire ({_html.escape(kind)})."
        if kind
        else "Scegli la coppia di unità, poi scrivi il numero."
    )
    extra = f"\n\n<b>{_html.escape(result)}</b>" if result else ""
    return _card(
        "🔄 <b>CONVERSIONI</b>",
        wait,
        extra,
    )


def compass_hub_text() -> str:
    return _card(
        "🧭 <b>BUSSOLA</b>",
        "Dentro STRUMENTI. Posizione e direzione, non un navigatore stradale.",
        "📍 <b>POSIZIONE GPS</b> — coordinate, quota del terreno, declinazione, mappa\n"
        "🧭 <b>BUSSOLA</b> — nord geografico e nord magnetico in quel punto\n"
        "🎯 <b>VERSO UN LUOGO</b> — distanza in linea d'aria e azimut\n\n"
        "Puoi scrivere una città. Se non la dici, uso Cuneo.",
    )


def world_mondi_text() -> str:
    return _card(
        "🚀 <b>STUDIA LO SPAZIO</b>",
        "Enciclopedia: Wikipedia e Wikidata. Niente oracoli, niente salvati, niente casuale.",
        "☀️ Sistema Solare · 🌑 Lune · 🧊 Nani · ☄️ Comete · 🪨 Asteroidi\n"
        "⭐ Stelle · ✨ Costellazioni · 🌌 Galassie · 🌀 Nebulose\n"
        "🕳️ Buchi neri · 🔭 Cielo profondo · 🪐 Esopianeti · ⭐ Sistemi\n"
        "👽 Vita · 🚀 Missioni · 📡 Sonde · 🛰️ Satelliti · ☀️ Sole · 📚 Impara\n\n"
        "Oceanici e abitabili, dove compaiono, sono modelli di raggio e temperatura: non oceani e non vita.",
    )


def watch_sats_hub_text(place: str = "") -> str:
    where = (
        f"Città salvata: <b>{_html.escape(place)}</b>. I passaggi sopra quella città non li calcolo."
        if place
        else "I passaggi sopra una città non li calcolo."
    )
    return _card(
        "🛰️ <b>SATELLITI</b>",
        "Posizioni live, adesso. L'enciclopedia Wikipedia sta in Studia lo spazio.",
        f"{where}\n"
        "🛰️ <b>ISS</b> — Where the ISS at? (NORAD 25544)\n"
        "👥 <b>CHI È LASSÙ</b> — Open Notify\n"
        "🏠 <b>TIANGONG</b> · 🔭 <b>HUBBLE</b> — TLE live + SGP4\n"
        "🏠 <b>STAZIONI</b> — ISS e Tiangong insieme\n"
        "🌍 <b>OSSERVAZIONE TERRA</b> — Terra, Aqua, Landsat, Sentinel-2A\n"
        "🌦️ <b>METEO SAT</b> — NOAA-20, NOAA-21, GOES-16\n\n"
        "La visibilità ISS «al sole / in ombra» è geometria del satellite, non un avvistamento da terra. "
        "Non elenco Starlink.",
    )


def world_orbit_text() -> str:
    return watch_sats_hub_text()


def mondi_hub_text() -> str:
    return _card(
        "🌌 <b>ESPLORA I MONDI</b>",
        "Ogni filtro è una ricerca sull'archivio, o una voce Wikipedia.",
        "🌊 Oceanici e 🌱 abitabili = raggio e temperatura, non oceani e non vita.\n"
        "🌋 Vulcanici, 💍 anelli, 🌙 molte lune: corpi del Sistema Solare con voce.",
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
        "🌿 <b>NATURA</b>",
        "Bot di BOTSQUAD per la Terra. Flora, fauna e pietre, allo stesso livello.",
        "🌿 <b>FLORA</b> — eventi nel mondo, feed live, enciclopedia (mare, terra, vulcani, ghiaccio)\n"
        "🐾 <b>FAUNA</b> — ancora vuota. Gli animali arrivano dopo.\n"
        "💎 <b>PIETRE</b> — mineralogia, laboratorio, collezione",
    )


def world_flora_text() -> str:
    return _card(
        "🌿 <b>FLORA</b>",
        "Terra, acqua, fuoco e ghiaccio. Niente animali: quelli stanno in Fauna, quando ci saranno.",
        "🌍 <b>EVENTI</b> — catastrofi e fenomeni importanti nel mondo, live\n"
        "📡 <b>LIVE</b> — scosse, eruzioni aperte, tempeste: ogni evento ha un link\n"
        "📖 <b>ESPLORA LA NATURA</b> — mari, oceani, terra, vulcani, placche, ghiacciai",
    )


def world_fauna_text() -> str:
    return _card(
        "🐾 <b>FAUNA</b>",
        "Qui arriveranno gli animali. Per ora la stanza è vuota, di proposito.",
        "Niente schede, niente elenchi, niente API. "
        "Flora e Pietre sono le altre due porte di NATURA.",
    )


def world_natura_text() -> str:
    return _card(
        "📖 <b>ESPLORA LA NATURA</b>",
        "Enciclopedia Wikipedia / Wikidata. Mari, oceani, terra, vulcani, placche, ghiacciai. Niente animali.",
        "🌍 Terra — crosta, mantello, nucleo, atmosfera, tettonica\n"
        "🌊 Oceani — i cinque oceani, fosse, correnti\n"
        "🌊 Mari — Mediterraneo e gli altri mari\n"
        "🔥 Vulcani — schede di edifici noti, non un bollettino eruttivo\n"
        "🧭 Placche — tettonica\n"
        "🧊 Ghiacciai — calotte, criosfera, ghiacciai con voce\n\n"
        "Apro la voce, non la riscrivo. Pietre e Fauna stanno al piano di NATURA, non qui.",
    )


def world_live_text() -> str:
    return _card(
        "📡 <b>LIVE</b>",
        "Cataloghi aperti adesso. Ogni evento ha una riga di senso e un link alla fonte. Niente Wikipedia.",
        "📅 <b>Scosse</b> — USGS: ultime 24 ore, 7 giorni, o solo quelle importanti\n"
        "🌋 <b>Eruzioni aperte</b> — vulcani che NASA sta ancora seguendo, non le schede di Esplora\n"
        "🌀 <b>Cicloni e tempeste</b> — tifoni e uragani ancora aperti\n"
        "🔥 Incendi · 🧊 Ghiaccio · 🌊 Alluvioni · 🪨 Frane · 🌵 Siccità\n"
        "📋 Tutti i fenomeni — l'elenco misto, sempre con link\n\n"
        "Non è un'allerta della protezione civile.",
    )


def world_ocean_text() -> str:
    return _card(
        "🌊 <b>OCEANI</b>",
        "I grandi bacini e le correnti. Voci Wikipedia, non un atlante inventato.",
        "Pacifico, Atlantico, Indiano, Artico, Australe, Fossa delle Marianne, Corrente del Golfo.",
    )


def world_sea_text() -> str:
    return _card(
        "🌊 <b>MARI</b>",
        "Mari con voce. Wikipedia / Wikidata, niente carte nautiche inventate.",
        "Mediterraneo, Adriatico, Tirreno, Nero, Rosso, Baltico, del Nord, Caraibi, Caspio.",
    )


def world_ice_text() -> str:
    return _card(
        "🧊 <b>GHIACCIAI</b>",
        "Calotte, criosfera, ghiacciai noti. Voci, non un bollettino sul disgelo.",
        "Antartide, Groenlandia, Perito Moreno, Aletsch, Vatnajökull, Khumbu, Forni.",
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
        "Tocca un nome. Per gli eventi aperti in questo momento: 📡 Live.",
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
        "Mineralogia da catalogo, nel bot NATURA. Il folklore sta in ORACOLO, a parte.",
        "Foto: pietra al centro, tavolo uniforme. Non è un'analisi.\n\n"
        "🧭 Esplora · 🔬 Laboratorio · 🎒 Collezione · 🧠 Giochi",
    )


def world_miss_text() -> str:
    return _card(
        "🚀 <b>MISSIONI</b>",
        "Voli veri, sonde, lezioni e una sfida al giorno.",
        "Schede delle missioni, astronauti, quiz a quattro livelli.",
    )


def quiz_hub_text() -> str:
    return _card(
        "🧩 <b>QUIZ</b>",
        "Un bot a parte. Scegli il mondo, poi l'argomento. Le domande restano nel recinto di quel bot.",
        "🔮 ORACOLO — segni, rune, Lenormand (niente letture)\n"
        "🔭 ASTRO — sistema solare, lune, enciclopedia live\n"
        "🌿 NATURA — pietre, terra, vulcani, oceani\n"
        "🧰 STRUMENTI — calcoli, conversioni, cardinali\n\n"
        "La classifica è solo tua. I mondi non si mescolano.",
    )


def quiz_world_text(wid: str) -> str:
    from services.squadquiz import WORLD_META, canonical_wid, topics_of

    meta = WORLD_META.get(canonical_wid(wid)) or {"emoji": "🧩", "name": wid.upper(), "blurb": ""}
    lines = [f"{label}" for _tid, label in topics_of(wid)]
    body = "\n".join(lines) if lines else "Questo mondo non ha ancora argomenti."
    return _card(
        f"{meta['emoji']} <b>QUIZ · {meta['name']}</b>",
        str(meta.get("blurb") or "Scegli un argomento."),
        body,
    )
