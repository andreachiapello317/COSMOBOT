"""Testi di interfaccia della home a sette mondi. Non sono contenuti astronomici."""


def home_text() -> str:
    return (
        "🌌 <b>COSMOBOT</b>\n\n"
        "Esplorare sé stessi, il cielo e l'universo. Sette mondi, un filo.\n\n"
        "🔮 <b>TE STESSO</b> — tema, oroscopo, transiti, compatibilità, specchio, rituale\n"
        "🔮 <b>ORACOLI</b> — tarocchi, I Ching, rune, Lenormand, pietre\n"
        "🔭 <b>CIELO</b> — cosa vedi adesso, stelle, eventi, cielo profondo\n"
        "🪐 <b>MONDI</b> — esploratore: esopianeti, sistemi, salvataggi\n"
        "👽 <b>VITA</b> — esopianeti, zona abitabile, SETI\n"
        "🚀 <b>MISSIONI</b> — sonde, quiz, missione del giorno\n"
        "💎 <b>PIETRE</b> — minerali, gemme, laboratorio, collezione\n\n"
        "✨ <b>COSMICO</b> — un pezzo da ogni mondo.\n"
        "🎲 <b>CASUALE</b> — carta, cielo o sonda."
    )


def esplora_text() -> str:
    return (
        "🧭 <b>ESPLORA</b>\n\n"
        "Sette mondi. Tocca quello che vuoi aprire.\n\n"
        "🔮 Te stesso — carta e rituali interiori\n"
        "🔮 Oracoli — tradizionali, mazzi COSMOBOT e pietre\n"
        "🔭 Cielo — astronomia reale, adesso e sopra di te\n"
        "🪐 Mondi — Sistema Solare, esopianeti, sistemi stellari\n"
        "👽 Vita — come la cerchiamo, senza dichiararla\n"
        "🚀 Missioni — voli, lezioni, sfide del giorno\n"
        "💎 Pietre — scienza, geologia, storia; il simbolismo sta a parte"
    )


def domanda_text() -> str:
    return lettura_text()


def lettura_text() -> str:
    return (
        "📖 <b>LETTURA</b>\n\n"
        "Scrivi cosa sta succedendo — una frase basta.\n"
        "Poi scegli lo strumento, o lascia che lo scelga COSMOBOT.\n\n"
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n"
        "🎲 Sorprendimi — pesco io il metodo.\n\n"
        "È una lettura simbolica, non una previsione certa."
    )


def oracoli_text() -> str:
    return (
        "🔮 <b>ORACOLI</b>\n\n"
        "Scegli lo strumento. I mazzi COSMOBOT stanno in un menu a parte.\n\n"
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n"
        "🧿 Mazzi · 🪞 Sì/No · 📖 Lettura · 💎 Pietre\n"
        "🎲 Sorprendimi — pesco io il metodo."
    )


def rune_intro_text() -> str:
    return (
        "🪶 <b>RUNE</b>\n\n"
        "Le 24 rune dello Elder Futhark. I nomi sono quelli storici; "
        "i significati sono il dataset interno, non un oracolo infallibile.\n\n"
        "Pensa a una domanda. Non deve essere sì/no.\n\n"
        "Quando l'hai formulata, premi il pulsante."
    )


def world_self_text() -> str:
    return (
        "🔮 <b>TE STESSO</b>\n\n"
        "Tema natale, oroscopo, transiti, compatibilità.\n"
        "Più due pratiche simboliche: specchio e rituale lunare.\n"
        "I segni e la sinastria sono tradizione, non astronomia."
    )


def compat_hub_text(*, has_natal: bool, has_syn: bool = False) -> str:
    extra = (
        "🌌 <b>Sinastria</b> — due temi live, aspetti tra le carte.\n"
        if has_natal
        else "Per sinastria e overlay serve il 🌌 tema salvato.\n"
    )
    overlay = "🏠 <b>Overlay</b> — i loro pianeti nelle tue case.\n" if has_syn else ""
    return (
        "❤️ <b>COMPATIBILITÀ</b>\n\n"
        "Più porte, nessuna percentuale. Tutto è tradizione, non astronomia.\n\n"
        "☀️ Soli · 🌙 Lune · ⬆️ Ascendenti · ☿️ Mercurio\n"
        "♀️♂️ Venere e Marte · 🔥 Elementi · ☀️🌙⬆️ Big Three\n"
        f"{extra}{overlay}\n"
        "Se hai il tema, i tuoi punti li prendo dalla carta. "
        "Non è una previsione e non sostituisce due persone che si parlano."
    )


def world_div_text() -> str:
    return oracoli_text()


def world_sky_text() -> str:
    return (
        "🔭 <b>CIELO</b>\n\n"
        "Astronomia reale. Gli oracoli stanno nell'altro mondo.\n\n"
        "🔭 Adesso · 🌙 Luna · 🪐 Pianeti · ⭐ Stelle\n"
        "🌠 Eventi · 📚 Cataloghi (nani, comete, profondo)\n"
        "🌅 Alba · 🛰️ ISS\n\n"
        "Numeri da mappa del cielo, Skytime, Wikidata e NASA. "
        "Niente visibilità inventata."
    )


def world_mondi_text() -> str:
    return (
        "🪐 <b>MONDI</b>\n\n"
        "Un esploratore, non un oracolo.\n\n"
        "🌍 Filtri NASA · ⭐ Sistemi · ☀️ Sistema Solare\n"
        "🪐 Pianeti e lune · 🪨 Asteroidi · 📌 Salvati\n\n"
        "Oceanici e abitabili = modelli, non oceani e non vita."
    )


def mondi_hub_text() -> str:
    return (
        "🌌 <b>ESPLORA I MONDI</b>\n\n"
        "Ogni filtro è una ricerca sull'archivio NASA, oppure una scheda Wikipedia.\n"
        "🌊 Oceanici e 🌱 abitabili = fasce di raggio e temperatura, non oceani e non vita.\n"
        "🌋 Vulcanici, 💍 anelli, 🌙 molte lune: corpi del Sistema Solare con voce.\n"
        "🌑 Senza stella: se l'archivio è vuoto, apro la voce sui pianeti erranti.\n"
        "🎲 Genera = mondo immaginario, scritto grande che è finto."
    )


def cosmo_text() -> str:
    return (
        "🌌 <b>COSMO</b>\n\n"
        "Sopra i mondi: una mappa dell'universo osservabile, da cataloghi live.\n\n"
        "⭐ Stelle · 🪐 Sistemi · 🌍 Mondi\n"
        "🌌 Galassie · 🌀 Nebulose · 🕳️ Buchi neri\n"
        "💥 Supernovae · 🔭 Cielo profondo\n\n"
        "Non mescola gli oracoli. Solo astronomia e schede Wikipedia/NASA."
    )


def sistemi_text() -> str:
    return (
        "⭐ <b>SISTEMI STELLARI</b>\n\n"
        "Una stella ospite, i suoi pianeti nell'archivio, un albero. "
        "Niente lune extrasolari: l'archivio quasi non le ha.\n"
        "Il Sistema Solare resta la scheda Wikidata, non uno scarico JPL."
    )


def life_plus_text() -> str:
    return (
        "🧬 <b>E SE CI FOSSE VITA?</b>\n\n"
        "Due piani, tenuti distinti.\n\n"
        "<b>Osservato / documentato</b> — voci Wikipedia: SETI, firme biologiche, "
        "estremofili, zona abitabile, oceani sotto il ghiaccio.\n\n"
        "<b>Speculazione</b> — il paradosso di Fermi è un argomento, "
        "non una rivelazione. I candidati HZ sono un filtro numerico.\n\n"
        "COSMOBOT non dichiara vita su nessun mondo."
    )


def world_vita_text() -> str:
    return (
        "👽 <b>VITA</b>\n\n"
        "Come cerchiamo la vita: oceani sotto il ghiaccio, esopianeti, SETI, biosignature.\n"
        "I candidati in zona abitabile sono un filtro di modelli, non mondi abitati."
    )


def world_pietre_text() -> str:
    return pietre_hub_text()


def pietre_hub_text() -> str:
    return (
        "💎 <b>PIETRE</b>\n\n"
        "Mineralogia da catalogo. Il simbolismo sta a parte.\n"
        "Foto: pietra al centro, tavolo uniforme. Non è un'analisi.\n\n"
        "🧭 Esplora · 🔬 Laboratorio · ✨ Oracolo · 🧠 Giochi"
    )


def world_miss_text() -> str:
    return (
        "🚀 <b>MISSIONI</b>\n\n"
        "Schede delle missioni e delle sonde, astronauti, mini-lezioni,\n"
        "quiz a quattro difficoltà e la missione del giorno."
    )
