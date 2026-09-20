"""Petit Lenormand, 36 carte. Nomi tradizionali; testi del dataset, non un oracolo infallibile."""

from __future__ import annotations

import random
from typing import Any

LENORMAND: tuple[dict[str, str], ...] = (
    {"id": "rider", "num": "1", "emoji": "🏇", "it": "Il Cavaliere", "keys": "notizie · movimento · arrivo", "meaning": "Qualcosa si muove verso di te: un messaggio, una visita, un inizio. L'attesa si accorcia.", "pair": "Porta un annuncio o un incontro in ciò che segue."},
    {"id": "clover", "num": "2", "emoji": "🍀", "it": "Il Quadrifoglio", "keys": "fortuna lieve · occasione · sollievo", "meaning": "Una fortuna piccola ma vera. Non è la lotteria: è un respiro, un sì inatteso, un ostacolo che si sposta.", "pair": "Addolcisce e sblocca la carta accanto."},
    {"id": "ship", "num": "3", "emoji": "🚢", "it": "La Nave", "keys": "viaggio · lontananza · commercio", "meaning": "Partenza, distanza, affare oltre il recinto abituale. Qualcosa arriva da lontano o ti chiede di muoverti.", "pair": "Allontana o mette in viaggio il tema vicino."},
    {"id": "house", "num": "4", "emoji": "🏠", "it": "La Casa", "keys": "focolare · base · famiglia", "meaning": "La base: casa, famiglia, ciò che ti contiene. Chiede stabilità, non fuga.", "pair": "Radica il discorso nella vita quotidiana e nelle mura."},
    {"id": "tree", "num": "5", "emoji": "🌳", "it": "L'Albero", "keys": "salute · radici · tempo lungo", "meaning": "Crescita lenta, salute, lignaggio. Ciò che dura. Non forzare i tempi.", "pair": "Dà profondità e durata alla carta seguente."},
    {"id": "clouds", "num": "6", "emoji": "☁️", "it": "Le Nuvole", "keys": "confusione · dubbio · nebbia", "meaning": "Non vedi chiaro. Aspetta prima di decidere: la nebbia è temporanea, ma ora è nebbia.", "pair": "Offusca o rende instabile ciò che tocca."},
    {"id": "snake", "num": "7", "emoji": "🐍", "it": "Il Serpente", "keys": "complicazione · seduzione · curva", "meaning": "Una via non dritta: tentazione, inganno, o intelligenza che serpeggia. Occhio alle intenzioni.", "pair": "Complica o rende ambigua la carta vicina."},
    {"id": "coffin", "num": "8", "emoji": "⚰️", "it": "La Bara", "keys": "fine · svuotamento · passaggio", "meaning": "Qualcosa termina. Non è necessariamente morte: è un coperchio che si chiude, e poi lo spazio vuoto.", "pair": "Chiude o trasforma in modo definitivo il tema accanto."},
    {"id": "bouquet", "num": "9", "emoji": "💐", "it": "Il Mazzo", "keys": "dono · bellezza · invito", "meaning": "Un gesto gentile, un invito, qualcosa che abbellisce. Accogliere senza sospetto eccessivo.", "pair": "Porta dono, cortesia o riconoscimento."},
    {"id": "scythe", "num": "10", "emoji": "⚔️", "it": "La Falce", "keys": "taglio · decisione rapida · rischio", "meaning": "Si taglia. Decisione secca, pericolo breve, raccolta. Meglio un colpo netto che un strappo lento.", "pair": "Accelera e recide ciò che segue."},
    {"id": "whip", "num": "11", "emoji": "🪢", "it": "La Frusta", "keys": "conflitto · ripetizione · discussione", "meaning": "Tensione, parole che tornano, un nodo che si riapre. Serve ritmo, non volume.", "pair": "Agita e ripete il tema vicino."},
    {"id": "birds", "num": "12", "emoji": "🐦", "it": "Gli Uccelli", "keys": "chiacchiere · nervosismo · doppio", "meaning": "Due voci, una chiamata, agitazione mentale. Parlare aiuta se non diventa rumore.", "pair": "Mette in dialogo o in ansia la carta accanto."},
    {"id": "child", "num": "13", "emoji": "🧒", "it": "Il Bambino", "keys": "inizio · ingenuità · piccolo", "meaning": "Qualcosa di nuovo e ancora fragile. Curiosità, o un lato di te che non ha imparato a fingere.", "pair": "Rimpicciolisce, inizia o rinnova."},
    {"id": "fox", "num": "14", "emoji": "🦊", "it": "La Volpe", "keys": "prudenza · strategia · lavoro", "meaning": "Attento alle intenzioni — tue e altrui. Intelligenza tattica, mestiere, non farti usare.", "pair": "Chiede astuzia e verifica sul tema vicino."},
    {"id": "bear", "num": "15", "emoji": "🐻", "it": "L'Orso", "keys": "forza · tutela · potere", "meaning": "Una forza grande: autorità, corpo, protezione. Può nutrire o schiacciare. Misura il peso.", "pair": "Amplifica potere e tutela."},
    {"id": "stars", "num": "16", "emoji": "⭐", "it": "Le Stelle", "keys": "speranza · guida · chiarezza", "meaning": "Una direzione notturna. Fiducia, ispirazione, un obiettivo che orienta senza urlare.", "pair": "Illumina e dà senso al vicino."},
    {"id": "stork", "num": "17", "emoji": "🦩", "it": "La Cicogna", "keys": "cambiamento · trasferimento · nascita", "meaning": "Un cambio di nido: casa, ruolo, stagione. Il nuovo arriva perché il vecchio è stretto.", "pair": "Porta transizione e spostamento."},
    {"id": "dog", "num": "18", "emoji": "🐕", "it": "Il Cane", "keys": "lealtà · amico · alleanza", "meaning": "Qualcuno (o una parte di te) resta. Amicizia, fedeltà, un sì che non negozia ogni giorno.", "pair": "Rende leale e vicino il tema."},
    {"id": "tower", "num": "19", "emoji": "🏰", "it": "La Torre", "keys": "istituzione · distanza · confine", "meaning": "Ufficio, regola, solitudine alta. Protegge e isola. Chiediti se il muro serve ancora.", "pair": "Istituzionalizza o allontana."},
    {"id": "garden", "num": "20", "emoji": "🌺", "it": "Il Giardino", "keys": "sociale · pubblico · rete", "meaning": "La piazza: gente, eventi, visibilità. Non è intimo. È dove ti vedono.", "pair": "Porta il discorso in pubblico."},
    {"id": "mountain", "num": "21", "emoji": "⛰️", "it": "La Montagna", "keys": "ostacolo · attesa · massa", "meaning": "Un blocco. Non si scava in un giorno. Gira, prepara, o accetta il tempo della salita.", "pair": "Rallenta e interpone un ostacolo."},
    {"id": "paths", "num": "22", "emoji": "🛣️", "it": "I Sentieri", "keys": "scelta · bivio · alternative", "meaning": "Due (o più) strade. Scegliere è già un atto. Restare fermi è una terza via, e costa.", "pair": "Apre un bivio sul tema accanto."},
    {"id": "mice", "num": "23", "emoji": "🐭", "it": "I Topi", "keys": "perdita · usura · preoccupazione", "meaning": "Qualcosa si consuma a morsi piccoli: soldi, fiducia, tempo. Trova la falla.", "pair": "Erode e preoccupa."},
    {"id": "heart", "num": "24", "emoji": "❤️", "it": "Il Cuore", "keys": "amore · affetto · centro", "meaning": "Il sentire. Amore, amicizia calda, ciò che ti è caro. Non intellettualizzare troppo.", "pair": "Colora di affetto e di coinvolgimento."},
    {"id": "ring", "num": "25", "emoji": "💍", "it": "L'Anello", "keys": "patto · ciclo · impegno", "meaning": "Un accordo, un legame, un ritorno. Promesse che tengono — o che stringono.", "pair": "Lega e ciclizza la carta vicina."},
    {"id": "book", "num": "26", "emoji": "📖", "it": "Il Libro", "keys": "segreto · studio · non detto", "meaning": "Qualcosa non è ancora aperto. Sapere, formazione, un capitolo chiuso. Non forzare la copertina.", "pair": "Nasconde o chiede di studiare."},
    {"id": "letter", "num": "27", "emoji": "✉️", "it": "La Lettera", "keys": "messaggio · documento · parola", "meaning": "Una comunicazione concreta: mail, contratto, notizia scritta. Leggi due volte.", "pair": "Porta un messaggio sul tema."},
    {"id": "man", "num": "28", "emoji": "👨", "it": "Il Signore", "keys": "figura maschile · io / lui", "meaning": "Una persona maschile, o il polo attivo della situazione. Chi agisce, chi decide.", "pair": "Personalizza al maschile o all'azione."},
    {"id": "woman", "num": "29", "emoji": "👩", "it": "La Dama", "keys": "figura femminile · io / lei", "meaning": "Una persona femminile, o il polo ricettivo. Chi accoglie, chi sente, chi tiene il campo.", "pair": "Personalizza al femminile o all'accoglienza."},
    {"id": "lilies", "num": "30", "emoji": "🤍", "it": "I Gigli", "keys": "pace · maturità · sensualità lenta", "meaning": "Calma, rispetto, un piacere senza fretta. Anzianità interiore. Niente urla.", "pair": "Pacifica e matura."},
    {"id": "sun", "num": "31", "emoji": "☀️", "it": "Il Sole", "keys": "successo · calore · evidenza", "meaning": "Luce piena. Ciò che funziona, che si vede, che scalda. Non nascondere il risultato.", "pair": "Rende evidente e favorevole."},
    {"id": "moon", "num": "32", "emoji": "🌙", "it": "La Luna", "keys": "emozione · fama · ciclo", "meaning": "Maree interiori, riconoscimento, creatività notturna. Segui il ciclo, non l'orologio.", "pair": "Aggiunge emozione, immagine, ritmo lunare."},
    {"id": "key", "num": "33", "emoji": "🗝️", "it": "La Chiave", "keys": "soluzione · accesso · sì decisivo", "meaning": "Si apre. Una risposta, un permesso, il pezzo che faceva funzionare il resto.", "pair": "Sblocca e conferma."},
    {"id": "fish", "num": "34", "emoji": "🐟", "it": "I Pesci", "keys": "denaro · flusso · abbondanza", "meaning": "Risorse che circolano: soldi, idee, opportunità. Non bloccare il flusso per paura.", "pair": "Porta materia, denaro, circolazione."},
    {"id": "anchor", "num": "35", "emoji": "⚓", "it": "L'Ancora", "keys": "stabilità · lavoro · restare", "meaning": "Fermarsi di proposito. Lavoro solido, fedeltà a un porto. Attenzione a non arrugginire.", "pair": "Fissa e rende duraturo."},
    {"id": "cross", "num": "36", "emoji": "✝️", "it": "La Croce", "keys": "prova · dovere · peso", "meaning": "Un carico che ha senso solo se lo riconosci. Fede, prova, ciò che non si può delegare.", "pair": "Aggiunge peso, prova o significato alto."},
)

SPREADS: dict[str, dict[str, Any]] = {
    "1": {"count": 1, "title": "1 carta", "positions": ("Il tema",)},
    "3": {"count": 3, "title": "3 carte", "positions": ("Passato / causa", "Presente", "Sviluppo")},
    "5": {"count": 5, "title": "5 carte", "positions": ("Contesto", "Tu", "Gli altri", "Attenzione", "Esito")},
    "9": {
        "count": 9,
        "title": "9 carte",
        "positions": (
            "Passato remoto",
            "Influenza",
            "Futuro remoto",
            "Passato recente",
            "Centro",
            "Futuro prossimo",
            "Tu",
            "Ambiente",
            "Esito",
        ),
    },
}


def draw_lenormand(count: int) -> list[dict[str, str]]:
    count = max(1, min(count, 9))
    pool = list(LENORMAND)
    random.shuffle(pool)
    return [dict(card) for card in pool[:count]]


HINTS: dict[str, tuple[str, ...]] = {
    "1": ("Il tema di questa pesca.",),
    "3": ("Da dove viene.", "Dov'è ora.", "Dove può andare."),
    "5": (
        "Lo sfondo.",
        "Tu, in mezzo.",
        "Gli altri.",
        "Cosa merita attenzione.",
        "Verso dove tende.",
    ),
    "9": (
        "Lontano, dietro.",
        "Chi o cosa influenza.",
        "Lontano, davanti.",
        "Appena lasciato.",
        "Il centro, ora.",
        "Il prossimo passo.",
        "Tu.",
        "Chi ti sta intorno.",
        "L'esito, se resti così.",
    ),
}


def combine_pair(left: dict[str, str], right: dict[str, str]) -> str:
    return f"{left['emoji']} {left['it']} → {right['emoji']} {right['it']}\n{left['pair']}"


def pair_lines(drawn: list[dict[str, str]], *, limit: int = 3) -> list[str]:
    rows: list[str] = []
    for idx in range(min(limit, max(0, len(drawn) - 1))):
        rows.append(combine_pair(drawn[idx], drawn[idx + 1]))
    return rows


def lenormand_closer(drawn: list[dict[str, str]]) -> str:
    if not drawn:
        return ""
    if len(drawn) == 1:
        card = drawn[0]
        return f"{card['it']}: {card['keys']}. Una carta, un tema."
    first, last = drawn[0], drawn[-1]
    return (
        f"Si parte da {first['it']} e si arriva a {last['it']}. "
        f"L'ultima carta è l'esito: {last['keys']}."
    )


def synthesize_lenormand(question: str, drawn: list[dict[str, str]]) -> str:
    if not drawn:
        return ""
    if len(drawn) == 1:
        return lenormand_closer(drawn)
    body = " ".join(pair_lines(drawn, limit=3))
    if question:
        return f"{body} {lenormand_closer(drawn)}"
    return f"{body} {lenormand_closer(drawn)}"
