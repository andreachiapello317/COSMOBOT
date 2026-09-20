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
        "Entra in un bot. 🏠 Inizio torna sempre qui.",
    )


def home_text() -> str:
    return all_hub_text()


def oracolo_hub_text() -> str:
    return _card(
        "🔮 <b>ORACOLO</b>",
        "Bot di BOTSQUAD per guardarsi dentro. Simboli, non telescopio.",
        "🔮 <b>TE STESSO</b> — tema, oroscopo, transiti, compatibilità, specchio, rituale\n"
        "🔮 <b>ORACOLI</b> — tarocchi, I Ching, rune, Lenormand, pietre (estrazione)\n\n"
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
        "Il cassetto degli strumenti. Tradizione e mazzi nostri, tutti simbolici.",
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n"
        "🧿 Mazzi · 🪞 Sì/No · 📖 Lettura · 💎 Pietre\n"
        "🎲 Sorprendimi — pesco io il metodo.",
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
        "La tua carta e i transiti. Tradizione astrologica, non astronomia.",
        "Tema natale, oroscopo, transiti, compatibilità.\n"
        "Più due pratiche: specchio e rituale lunare.",
    )


def compat_hub_text(*, has_natal: bool, has_syn: bool = False) -> str:
    extra = (
        "🌌 <b>Sinastria</b> — due temi live, aspetti tra le carte.\n"
        if has_natal
        else "Per sinastria e overlay serve il 🌌 tema salvato.\n"
    )
    overlay = "🏠 <b>Overlay</b> — i loro pianeti nelle tue case.\n" if has_syn else ""
    return _card(
        "❤️ <b>COMPATIBILITÀ</b>",
        "Due carte a confronto. Nessuna percentuale, nessuna previsione.",
        "☀️ Soli · 🌙 Lune · ⬆️ Ascendenti · ☿️ Mercurio\n"
        "♀️♂️ Venere e Marte · 🔥 Elementi · ☀️🌙⬆️ Big Three\n"
        f"{extra}{overlay}\n"
        "Se hai il tema, i tuoi punti li prendo dalla carta.",
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
