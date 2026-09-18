"""Testi di interfaccia della home a sei mondi. Non sono contenuti astronomici."""


def home_text() -> str:
    return (
        "🌌 <b>COSMOBOT</b>\n\n"
        "Esplorare sé stessi, il cielo e l'universo. Sei mondi, un filo.\n\n"
        "🔮 <b>TE STESSO</b> — tema, oroscopo, transiti, specchio, rituale\n"
        "🔮 <b>ORACOLI</b> — tarocchi, I Ching, rune, Lenormand, mazzi COSMOBOT\n"
        "🔭 <b>CIELO</b> — cosa vedi adesso, stelle, eventi, cielo profondo\n"
        "🪐 <b>MONDI</b> — pianeti, lune, asteroidi, buchi neri, galassie\n"
        "👽 <b>VITA</b> — esopianeti, zona abitabile, SETI\n"
        "🚀 <b>MISSIONI</b> — sonde, quiz, missione del giorno\n\n"
        "✨ <b>COSMICO</b> prende un pezzo da ogni mondo.\n"
        "🎲 <b>RANDOM</b> pesca nel sacco: carta, cielo o sonda."
    )


def esplora_text() -> str:
    return (
        "🧭 <b>ESPLORA</b>\n\n"
        "Sei mondi. Tocca quello che vuoi aprire.\n\n"
        "🔮 Te stesso — carta e rituali interiori\n"
        "🔮 Oracoli — tradizionali e mazzi COSMOBOT\n"
        "🔭 Cielo — astronomia reale, adesso e sopra di te\n"
        "🪐 Mondi — Sistema Solare e oltre\n"
        "👽 Vita — come la cerchiamo, senza dichiararla\n"
        "🚀 Missioni — voli, lezioni, sfide del giorno"
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
        "Scegli il tuo strumento.\n\n"
        "<b>Tradizionali</b>\n"
        "🃏 Tarocchi · ☯️ I Ching · 🪶 Rune · 🌿 Lenormand\n\n"
        "<b>COSMOBOT</b>\n"
        "🧿 Archetipi · 🐺 Animali · 🗝️ Simboli\n"
        "🌿 Elementi · 🪐 Pianeti · 🌙 Luna\n\n"
        "🪞 Sì/No · 🕯️ Domanda · 📖 Lettura\n"
        "🎲 Sorprendimi — pesco io quale oracolo usare."
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
        "Tema natale, oroscopo, transiti sul tema salvato.\n"
        "Più due pratiche simboliche: specchio e rituale lunare.\n"
        "Non sono misure astronomiche: sono domande che ti fai."
    )


def world_div_text() -> str:
    return oracoli_text()


def world_sky_text() -> str:
    return (
        "🔭 <b>CIELO</b>\n\n"
        "Astronomia reale. Gli oracoli stanno nell'altro mondo.\n\n"
        "🔭 <b>Adesso</b> — mappa testuale, visibile / sotto l'orizzonte\n"
        "🌍 Sistema — pianeti, nani, lune, comete, asteroidi, sciami\n"
        "⭐ Stelle e costellazioni — schede Wikipedia + cielo live\n"
        "🌠 Eventi — eclissi, sciami, attività solare, perigeo/apogeo\n"
        "🛰️ Profondo — Messier, nebulose, quasar, esopianeti\n\n"
        "I numeri arrivano da skymap.sh, Skytime, Wikidata, NASA. "
        "Niente visibilità inventata."
    )


def world_mondi_text() -> str:
    return (
        "🪐 <b>MONDI</b>\n\n"
        "Sistema Solare interattivo, pianeti nani, lune, comete,\n"
        "asteroidi vicini o nel tema, buchi neri, galassie.\n"
        "Masse, diametri e gravità arrivano da Wikidata."
    )


def world_vita_text() -> str:
    return (
        "👽 <b>VITA</b>\n\n"
        "Come cerchiamo la vita: oceani sotto il ghiaccio, esopianeti, SETI, biosignature.\n"
        "I candidati in zona abitabile sono un filtro di modelli, non mondi abitati."
    )


def world_miss_text() -> str:
    return (
        "🚀 <b>MISSIONI</b>\n\n"
        "Schede delle missioni e delle sonde, astronauti, mini-lezioni,\n"
        "quiz a quattro difficoltà e la missione del giorno."
    )
