"""Testi di interfaccia: BOTSQUAD, ORACOLO e ASTRO. I mondi non si mescolano."""


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
        "Due bot in un solo Telegram. Ognuno ha i suoi mondi, e non si mescolano.",
        "🔮 <b>ORACOLO</b> — te stesso, carte, rune, rituali.\n"
        "🔭 <b>ASTRO</b> — cielo vero, pianeti, missioni, pietre.\n\n"
        "Tutto a pulsanti. 📚 Aiuto spiega i mondi. 🏠 Inizio torna sempre qui.",
    )


def home_text() -> str:
    return all_hub_text()


def oracolo_hub_text() -> str:
    return _card(
        "🔮 <b>ORACOLO</b>",
        "Bot di BOTSQUAD per guardarsi dentro. Simboli, non telescopio.",
        "🔮 <b>TE STESSO</b> — oroscopo, tema natale, specchio, compatibilità\n"
        "🔮 <b>ORACOLI</b> — tarocchi, I Ching, rune, Lenormand, sì/no, pietre\n\n"
        "Il cielo misurato sta in 🔭 ASTRO.",
    )


def astro_hub_text() -> str:
    return _card(
        "🔭 <b>ASTRO</b>",
        "Bot di BOTSQUAD per il cielo vero. Cataloghi e numeri live, niente carte.",
        "🔭 <b>CIELO</b> — adesso, stelle, eventi, ISS\n"
        "🪐 <b>MONDI</b> — esopianeti, sistemi, salvataggi\n"
        "👽 <b>VITA</b> — come la cerchiamo, senza dichiararla\n"
        "🚀 <b>MISSIONI</b> — sonde, quiz, missione del giorno\n"
        "💎 <b>PIETRE</b> — mineralogia, laboratorio, collezione\n\n"
        "✨ COSMICO e 🎲 casuale pescano da questi mondi.",
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
        "🎲 Sorprendimi — pesco io il metodo.",
    )


def oracoli_text() -> str:
    return _card(
        "🔮 <b>ORACOLI</b>",
        "Sei strumenti, tutti simbolici. Nessun verdetto, nessuna astronomia.",
        "🃏 <b>Tarocchi</b> — mazzo live, spread a scelta\n"
        "☯️ <b>I Ching</b> — sei lanci, libro Wilhelm\n"
        "🪶 <b>Rune</b> — Elder Futhark, 1 o 3\n"
        "🌿 <b>Lenormand</b> — 36 sibille, 1/3/5/9\n"
        "🪞 <b>Sì / No</b> — un'inclinazione, non un verdetto\n"
        "💎 <b>Pietre</b> — estrazione simbolica, non mineralogia\n\n"
        "🎲 <b>Sorprendimi</b> — pesco uno strumento e ti do subito la lettura.",
    )


def rune_intro_text() -> str:
    return _card(
        "🪶 <b>RUNE</b>",
        "Ventiquattro segni dell'Elder Futhark. Nomi storici, significati nostri.",
        "Pensa a una domanda. Non deve essere sì/no.\n"
        "Quando l'hai formulata, premi il pulsante.",
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


def world_sky_text() -> str:
    return _card(
        "🔭 <b>CIELO</b>",
        "Cosa c'è sopra di te adesso. Numeri live, niente oracoli.",
        "🔭 Adesso · 🌙 Luna · 🪐 Pianeti · ⭐ Stelle\n"
        "🌠 Eventi · 📚 Cataloghi (nani, comete, profondo)\n"
        "🌅 Alba · 🛰️ ISS",
    )


def world_mondi_text() -> str:
    return _card(
        "🪐 <b>MONDI</b>",
        "Un esploratore NASA e Wikipedia. Non un oracolo.",
        "🌍 Filtri · ⭐ Sistemi · ☀️ Sistema Solare\n"
        "🪐 Pianeti e lune · 🪨 Asteroidi · 📌 Salvati\n\n"
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


def world_pietre_text() -> str:
    return pietre_hub_text()


def pietre_hub_text() -> str:
    return _card(
        "💎 <b>PIETRE</b>",
        "Mineralogia da catalogo. Il folklore sta nell'oracolo, a parte.",
        "Foto: pietra al centro, tavolo uniforme. Non è un'analisi.\n\n"
        "🧭 Esplora · 🔬 Laboratorio · ✨ Oracolo · 🧠 Giochi",
    )


def world_miss_text() -> str:
    return _card(
        "🚀 <b>MISSIONI</b>",
        "Voli veri, sonde, lezioni e una sfida al giorno.",
        "Schede delle missioni, astronauti, quiz a quattro livelli.",
    )
